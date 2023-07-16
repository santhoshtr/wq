from typing import Union

import numpy as np
from onnxruntime import InferenceSession
from transformers import (
    AutoConfig,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    QuestionAnsweringPipeline,
)
from transformers.modeling_outputs import QuestionAnsweringModelOutput

model_name = "distilbert-base-cased-distilled-squad"
tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained("models/onnx/tokenizer")
model_path = "models/onnx/model.onnx"


class BertForQuestionAnswering(PreTrainedModel):
    def __init__(self, model_name: str, model_path: str):
        config = AutoConfig.from_pretrained(model_name)
        super().__init__(config)
        self.model_name = model_name
        self.model_path = model_path
        self.session = InferenceSession(f"{model_path}")

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        token_type_ids: Union[None, np.int32] = None,
    ):
        inputs = {
            "input_ids": input_ids.numpy(),
            "attention_mask": attention_mask.numpy(),
        }
        if token_type_ids is not None:
            inputs["token_type_ids"] = token_type_ids.numpy()

        outputs = self.session.run(output_names=["start_logits", "end_logits"], input_feed=dict(inputs))
        return QuestionAnsweringModelOutput(start_logits=outputs[0], end_logits=outputs[1])


## ONNX MODEL
model: PreTrainedModel = BertForQuestionAnswering(model_name=model_name, model_path=model_path)
onnx_qa = QuestionAnsweringPipeline(model=model, tokenizer=tokenizer)
