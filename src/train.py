import argparse
import pickle

import pytorch_lightning as pl
import torch
from torch.utils import data

from data.make_dataset import reader, build_labels
from src.logger import logger
from src.model import ProtCNN
from src.utils import Lang, SequenceDataset


def get_argparse_arguments():
    # Create the parser
    parser = argparse.ArgumentParser(description='Train a model on the given dataset.')

    # Add the arguments
    parser.add_argument('--data_dir', type=str, default="data/random_split", help='Directory containing the data')
    parser.add_argument('--model_dir', type=str, default="model_weights", help='Directory to save the model')
    parser.add_argument('--gpu', action='store_true', help='Use GPU for training')
    parser.add_argument('--num_gpus', type=int, default=0, help='number of gpus to use')
    parser.add_argument('--cpu', action='store_true', help='Use CPU for training')
    parser.add_argument('--max_seq_len', type=int, default=120,
                        help='Max sequence length of protein (avoid changing this)')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size for training')
    parser.add_argument('--num_workers', type=int, default=0,
                        help='num_workers for training/test/validation dataloaders')
    parser.add_argument('--num_epochs', type=int, default=25, help='Number of epochs to train')
    parser.add_argument('--learning_rate', type=float, default=1e-2, help='Learning rate for the optimizer')
    parser.add_argument('--weight_decay', type=float, default=1e-2, help='Weight decay (L2 penalty)')
    parser.add_argument('--optimizer', type=str, default='SGD', help='Optimizer for training (Adam/SGD)')
    parser.add_argument('--momentum', type=float, default=0.9, help='Momentum for the optimizer')
    parser.add_argument('--seed', type=int, default=0, help='Random seed')

    parser.add_argument('--log_interval', type=int, default=100, help='Interval for logging')
    parser.add_argument('--eval_interval', type=int, default=500, help='Interval for evaluation')
    parser.add_argument('--save_interval', type=int, default=500, help='Interval for saving the model')
    parser.add_argument('--early_stopping', action='store_true', help='Use early stopping')
    parser.add_argument('--resume', type=str, help='Resume training from this checkpoint')
    parser.add_argument('--config', type=str, help='Configuration file')

    # Parse the arguments
    return parser.parse_args()


if __name__ == "__main__":

    # Runs argparse
    args = get_argparse_arguments()

    # Sets the seed
    pl.seed_everything(args.seed)

    # Sets the device
    if args.gpu and (torch.cuda.is_available() or torch.backends.mps.is_available()):
        device = "cuda" if torch.cuda.is_available() else "mps"
    else:
        if args.gpu:
            logger.info("Warning: --gpu is set but no GPU is found on this machine. Using CPU instead.")
        device = "cpu"
    logger.info(f"Device: {device}")

    # Reads data from data files.
    train_data, train_targets = reader("train", args.data_dir)
    valid_data, valid_targets = reader("dev", args.data_dir)
    test_data, test_targets = reader("test", args.data_dir)

    # Build integer correspondences for each label type in dataset.
    fam2label = build_labels(train_targets)  # fam2label is a dictionary mapping each family to a unique integer.

    # Build and get language.
    lang = Lang()
    word2id = lang.build_vocab(train_data)
    logger.info(f"AA dictionary formed. The length of dictionary is: {len(word2id)}.")

    # Create datasets.
    train_dataset = SequenceDataset(word2id, fam2label, args.max_seq_len, args.data_dir, "train")
    dev_dataset = SequenceDataset(word2id, fam2label, args.max_seq_len, args.data_dir, "dev")
    test_dataset = SequenceDataset(word2id, fam2label, args.max_seq_len, args.data_dir, "test")

    # save data for use during evaluation
    lang_params = {
        "word2id": word2id,
        "fam2label": fam2label,
        "max_seq_len": args.max_seq_len,
    }
    with open('lightning_logs/lang_params.pickle', 'wb') as handle:
        pickle.dump(lang_params, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Create dataloaders.
    dataloaders = dict()
    dataloaders['train'] = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        persistent_workers=True if args.num_workers > 0 else False,
    )
    dataloaders['dev'] = torch.utils.data.DataLoader(
        dev_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        persistent_workers=True if args.num_workers > 0 else False,
    )
    dataloaders['test'] = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        persistent_workers=True if args.num_workers > 0 else False,
    )
    logger.info(
        f"INPUT_SHAPE: {next(iter(dataloaders['test']))['sequence'].shape},"
        f" OUTPUT_SHAPE: {next(iter(dataloaders['test']))['target'].shape}"
    )

    # Create model.
    model = ProtCNN(
        num_classes=len(fam2label),
        learning_rate=args.learning_rate,
        optimizer=args.optimizer,
        weight_decay=args.weight_decay,
        momentum=args.momentum
    )

    # Train model
    trainer = pl.Trainer(accelerator=device, max_epochs=args.num_epochs, val_check_interval=1000)
    trainer.fit(model, dataloaders['train'], dataloaders['dev'])
