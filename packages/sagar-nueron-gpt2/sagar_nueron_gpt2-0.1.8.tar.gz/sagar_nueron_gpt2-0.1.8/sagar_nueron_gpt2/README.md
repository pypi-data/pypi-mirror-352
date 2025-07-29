
##  How to Run

###  Language & Framework

* **Language**: Python
* **Framework**: PyTorch

---

###  Installation

Make sure you have Python installed, then run the following commands to set up the environment:

```bash
pip install -i https://test.pypi.org/simple/ sagar-nueron-gpt2==0.1.7
pip install torch
pip install tiktoken
```

---

###  Train the Model

To train and save your GPT-2 model weights, run the following:

```python
from sagar_nueron_gpt2.TrainAndSaveGptWeights import Execute

exe = Execute()
exe.execute()
```

---

###  Inference from Trained Model

To run inference using the model you trained:

```python
from sagar_nueron_gpt2.inference_model import Inferencing

exe = Inferencing()
exe.inference()
```

---


