from src.model import ProtCNN
import argparse
import pickle
from src.utils import SequenceDataset
import torch

def get_argparse_arguments():
    # Create the parser
    parser = argparse.ArgumentParser(description='Train a model on the given dataset.')

    # Add the arguments
    parser.add_argument('--input_seq', type=str, default="NA", help='Input protein sequence')
    parser.add_argument('--model_checkpoint', type=str, default="lightning_logs/version_10/checkpoints/epoch=2-step=12738.ckpt", help='Directory for saved checkpoints')
    parser.add_argument('--lang_params', type=str, default="lightning_logs/lang_params.pickle", help='Language params file')
    parser.add_argument('--gpu', action='store_true', help='Use GPU for training')

    # Parse the arguments
    return parser.parse_args()


if __name__ == "__main__":

    # argument parser
    args = get_argparse_arguments()

    # Sets the device
    if args.gpu and (torch.cuda.is_available() or torch.backends.mps.is_available()):
        device = "cuda" if torch.cuda.is_available() else "mps"
    else:
        if args.gpu:
            print("Warning: --gpu is set but no GPU is found on this machine. Using CPU instead.")
        device = "cpu"
    print(f"Device: {device}")

    # Load model weight [Easier way]
    model = ProtCNN.load_from_checkpoint(args.model_checkpoint).to(device)

    # Get language params for encoding input.
    with open(args.lang_params, 'rb') as handle:
        lang_params = pickle.load(handle)

    # Construct language encoder and encoder input
    lang_encoder = SequenceDataset(lang_params["word2id"], lang_params["fam2label"], lang_params["max_seq_len"], None, None)
    x_encoded = lang_encoder.encode_single_sample(args.input_seq)
    x_encoded = x_encoded[0].reshape((1, 22, 120)).to(device)

    pred = model(x_encoded)
    print(pred)
