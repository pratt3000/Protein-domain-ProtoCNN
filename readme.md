# About
Protein domain prediction (for over 17000+ types of protein strings)

# How to run:

## Downloading

### Download data

Download the data from <a href="https://www.kaggle.com/googleai/pfam-seed-random-split">kaggle</a> and place it in a
folder.
It's expected that the folder structure is as follows:
```--data_dir = "data/random_split"```

```commandline
data
├── random_split
│   ├── dev
│   ├── test
│   ├── train

```

### Download Language Encoder

Download the language encoder from <a href="https://www.kaggle.com/googleai/pfam-seed-random-split">here</a> and place
it in a folder. <br>
```--lang_params = "path/to/lang_params/sample.pickle"```

### Download model checkpoints

Download any model checkpoint and put them in a folder. You can then specify the parameters as follows in scripts. <br>

```commandline
--model_checkpoint = "path/to/model_weights/sample.ckpt"
--lang_params = "path/to/lang_params/sample.pickle"
# and so on...
```

| Models                                                                            | Download link (weights)                                                                                 | test accuracy |
|-----------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|---------------|
| Default ProtoCNN                                                                  | <a href="https://drive.google.com/drive/folders/1lA6kCAmliLjnXIrbGhwNRSrR4cxWzb5S?usp=sharing">link</a> | 87.46%        |
| Default ProtoCNN + hyperparameter tuning                                          | <a href="https://drive.google.com/drive/folders/1pujYRdtBHDo8qjIcWNMUactUZkHlXaYs?usp=sharing">link</a> | 90.08%        |
| Custom Model (more details in [Model Specification](#custom-model-specification)) | <a href="https://drive.google.com/drive/folders/1HSPByzMYOPxCiWCT-eAXSsOtNDArLEOS?usp=sharing">link</a> | 92.31%        |

## Run using Docker

### Docker setup.

```commandline
docker build . -t instadeep:latest
```

### Open docker bash

```commandline
# CPU only
docker run --rm -it --entrypoint bash instadeep:latest

# GPU
docker run --rm -it --entrypoint bash --gpus=all instadeep:latest
```

### Visualize input data

```commandline
python src/visualizations/visualize.py --data_dir data/random_split --save_path reports/data_visualizations --partition "train"
```

Many other options are available as well, pl see ```python src/visualizations/visualize.py --help```

### Train model

(Note: batch_size needs to be much smaller on CPU (bs=1). To use GPU use the --gpu flag.) <br>

```commandline
python src/train.py --batch_size=256
```

Many other options are available as well, pl see ```python src/train.py --help```

### Visualize training metrics like loss, accuracy, etc.

```commandline
python src/visualizations/visualize_training_vals.py --metrics_file "path/to/file/sample.csv" --save_path "path/to/folder"
```

Many other options are available as well, pl see ```python src/visualizations/visualize.py --help```

### Get prediction for a single test sample

```commandline
python src/predict.py --input_seq="Protein_seq" --model_checkpoint="lightning_logs/version_10/checkpoints/epoch=2-step=12738.ckpt"
```

Many other options are available as well, pl see ```python src/predict.py --help```

### Evaluate trained model of test set

```commandline 
python src/evaluate.py --gpu --model_checkpoint="lightning_logs/version_10/checkpoints/epoch=2-step=12738.ckpt" --test_set_dir="data/random_split/test"
```

Many other options are available as well, pl see ```python src/evaluate.py --help```

## Run without docker

(Tested on Python version 3.10.13)

```commandline
# Install requirements (python 3.10)
pip install -r requirements.txt

# Export python path
export PYTHONPATH="${PYTHONPATH}:full/path/to/the/folder/Instadeep_takehome/"

"""Run any of the above commands now."""
```

# Testing

We will be using pytest for this.<br>

```commandline
# Run tests
coverage run -m pytest src/tests/

# Generate coverage report
coverage report -m
```

Generated Coverage report:<br>
<img src="reports/coverage_report/cr.png" alt="drawing" style="width:400px;"/>

# Visualize results in tensorboard

```commandline
# Run tensorboard by locating the tf_events file.
tensorboard --logdir=path/to/tensorboard/folder/sample_folder
```

# Custom Model Specification

1. I modified the architecture of the model by increasing the residual blocks, adding convolutional layers, increasing
   layer sizes and changing the input and output
   channels and made other small changes.
2. The model architecture is as follows: default proto_cNN (left), modified bigger model (right)
3. Note: To run the bigger model we'll have to do more changes like changes to the class ProtoCNN as well. It won't work
   out of box.

<p float="left">
   <img src="reports/model_arch/ProtoCNN_default.png" alt="drawing" style="width:400px;"/>
   <img src="reports/model_arch/Large_model_377M.png" alt="drawing" style="width:400px;"/> <br>
</p>
