# License Apache 2.0: (c) 2025 Yoan Sallami (Synalinks Team)

from typing import List

from synalinks.src.api_export import synalinks_export
from synalinks.src.backend import DataModel
from synalinks.src.backend import Instructions
from synalinks.src.backend import Prediction
from synalinks.src.modules.core.generator import Generator
from synalinks.src.modules.core.input_module import Input
from synalinks.src.optimizers.optimizer import Optimizer
from synalinks.src.programs import Program
from synalinks.src.saving import serialization_lib


class OPROOptimizedVariable(DataModel):
    predictions: List[Prediction] = []
    instructions: Instructions
    instructions_candidates: List[Instructions] = []


class OPROInputs(DataModel):
    predictions: List[Prediction] = []
    instructions_candidates: List[Instructions] = []


@synalinks_export("synalinks.optimizers.OPRO")
class OPRO(Optimizer):
    """Optimization by PROmpting (OPRO) optimizer

    Use a language model to optimize the prompt's instructions.

    Example:

    ```python
    import synalinks
    import asyncio

    async def main():
        # ... your program definition

        program.compile(
            reward=synalinks.rewards.ExactMatch(),
            optimizer=synalinks.optimizers.OPRO(
                language_model=language_model, # The language model to use
                k_best=10, # The number of best examples/instructions to provide to the LM
            ),
        )

        history = await program.fit(...)
    ```

    References:
        - [Large Language Models as Optimizers](https://arxiv.org/abs/2309.03409)

    Args:
        language_model (LanguageModel): The language model to use.
        k_best (int): The max number of best predictions and instructions
            to provide to the optimizer (default 10).
        opro_program (Program): The program to use. Optional.
            If None create one (non-trained) at start.
        name (str): The name of the optimizer.
        description (str): The description of the optimizer.
    """

    def __init__(
        self,
        language_model=None,
        k_best=10,
        opro_program=None,
        name=None,
        description=None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            description=description,
            data_model=OPROOptimizedVariable,
        )
        self.language_model = language_model
        self.k_best = k_best
        self.opro_program = opro_program

    async def build(self, variables):
        if not self.opro_program:
            opro_inputs = Input(data_model=OPROInputs)
            opro_outputs = await Generator(
                language_model=self.language_model,
                data_model=Instructions,
                instructions=[
                    "Your task is to generate instructions that maximize rewards.",
                    "Below are some previous instructions with their reward.",
                    "Generate instructions that is different from all the instructions.",
                    (
                        "The instructions should be concise, effective and generally"
                        " applicable to all predictions below."
                    ),
                ],
            )(opro_inputs)

            self.opro_program = Program(
                inputs=opro_inputs,
                outputs=opro_outputs,
                name="opro",
                description="OPRO Program",
            )
        self.built = True

    async def optimize(self, trainable_variable, reward=None):
        """Perform a backprop/optimization on a single variable."""
        # Backpropagate predictions reward
        predictions = trainable_variable.get("predictions")
        backpropagated_predictions = []
        backprop_pred_nb = 0
        for p in predictions:
            if p["reward"] is None:
                p["reward"] = reward
                backprop_pred_nb += 1
            backpropagated_predictions.append(p)
        if backprop_pred_nb > 0:
            trainable_variable.update({"predictions": backpropagated_predictions})
            # Backpropagate instructions reward
            instructions_predictions = trainable_variable.get("instructions_candidates")
            instructions = trainable_variable.get("instructions")
            instructions.update({"reward": reward})
            instructions_predictions.append(instructions)
            # Get the k best predictions (sorted by reward)
            sorted_predictions = sorted(
                backpropagated_predictions,
                key=lambda x: x["reward"] if x["reward"] is not None else float("-inf"),
                reverse=True,
            )
            top_k_predictions = sorted_predictions[: self.k_best]
            # Get the k best instructions (sorted by reward)
            sorted_instructions = sorted(
                trainable_variable.get("instructions_candidates"),
                key=lambda x: x["reward"] if x["reward"] is not None else float("-inf"),
                reverse=True,
            )
            top_k_instructions = sorted_instructions[: self.k_best]
            # Prepare inputs for OPRO
            inputs = OPROInputs(
                predictions=top_k_predictions,
                instructions_candidates=top_k_instructions,
            )
            new_instructions = await self.opro_program(inputs)
            trainable_variable.update({"instructions": new_instructions.get_json()})

    async def finalize(self, trainable_variable):
        """Finalize the optimization of a single variable (cleanup/scaling etc.)."""
        trainable_variable.update({"instructions_candidates": []})

    def get_config(self):
        config = {
            "k_best": self.k_best,
            "name": self.name,
            "description": self.description,
        }
        language_model_config = {
            "language_model": serialization_lib.serialize_synalinks_object(
                self.language_model,
            )
        }
        return {**config, **language_model_config}

    @classmethod
    def from_config(cls, config):
        language_model = serialization_lib.deserialize_synalinks_object(
            config.pop("language_model"),
        )
        return cls(language_model=language_model, **config)
