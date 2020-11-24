import argparse
import functools
import sys

from src.extractor import run_extractor
from src.learning import run_train, run_evaluation
from src.preprocess import run_preprocess, run_summary


class FlagDetectionTrainer:

    def __init__(self):
        actions = ["extract", "preprocess", "summary",
                   "train", "tune", "evaluate"]
        actions_desc = functools.reduce(lambda a, b: a + "\n\t" + b, actions)
        parser = argparse.ArgumentParser(
            description="Train a compiler and optimization detector",
            usage=f"{sys.argv[0]} <action> [<args>]\n"
                  f"Possible actions "
                  f"are:\n\t{actions_desc}",
            add_help=False)
        parser.add_argument("action",
                            choices=actions,
                            help="The action that should be performed.")
        args = parser.parse_args(sys.argv[1:2])
        # dispatch function with same name of the action
        getattr(self, args.action)(sys.argv[2:])

    @staticmethod
    def extract(args):
        parser = argparse.ArgumentParser(
            description="Extracts the unprocessed data from a binary file.",
            usage=f"{sys.argv[0]} extract [optional arguments] file "
                  f"output_dir\n"
        )
        parser.add_argument("input",
                            nargs="*",
                            metavar="file",
                            help="Binary file(s) that should be used for data"
                                 "extraction.")
        parser.add_argument("output_dir",
                            help="Folder that will be used for writing the "
                                 "extracted data.")
        parser.add_argument("-F", "--function", required=False,
                            choices=["true", "false"],
                            default="False",
                            help="Extracts data for function grained "
                                 "analysis if this variable is true.")
        parsed_args = parser.parse_args(args)
        run_extractor(parsed_args.input, parsed_args.output_dir,
                      bool(parsed_args.function == "true"))

    @staticmethod
    def preprocess(args):
        parser = argparse.ArgumentParser(
            description="Creates the train and test dataset from the "
                        "existing data.",
            usage=f"{sys.argv[0]} preprocess [optional arguments] -i data_dir "
                  f"-c "
                  f"category -m model_dir\n")
        parser.add_argument(metavar="data_dir",
                            help="Path to the folder containing the "
                                 "unprocessed data.")
        parser.add_argument(metavar="model_dir",
                            help="Path to the folder that will contain the "
                                 "model. If an existing dataset is found, "
                                 "it will be merged with this one.")
        parser.add_argument("-F", "--function", required=False,
                            choices=["true", "false"],
                            default="false",
                            help="Enables the function grained analysis.")
        parser.add_argument("-f", "--features", default=2048,
                            help="Number of features used in the evaluation, "
                                 "defaults to 2048.")
        parser.add_argument("-c", "--category", required=True, metavar="int",
                            help="A number representing the "
                                 "category label for this data.")
        parser.add_argument("-s", "--split", default=0.5,
                            help="The proportion between train, test and "
                                 "validation. The first split is between "
                                 "train and test+validation, the second "
                                 "between test and validation, using the "
                                 "same ratio.")
        parsed_args = parser.parse_args(args)
        run_preprocess(parsed_args.input, int(parsed_args.category),
                       parsed_args.model, bool(parsed_args.function == "true"),
                       int(parsed_args.features), float(parsed_args.split))

    @staticmethod
    def train(args):
        parser = argparse.ArgumentParser(
            description="Train (or resume training) a model using the "
                        "previously generated data.",
            usage=f"{sys.argv[0]} train [optional args] -m model_dir\n")
        parser.add_argument(metavar="model_dir",
                            help="Folder for the model containing the "
                                 "test.bin and train.bin generated by the "
                                 "preprocess action or a previous train run.")
        parser.add_argument("-n", "--network",
                            default="cnn", choices=["dense", "lstm", "cnn"],
                            help="Choose which network to use for training.")
        parser.add_argument("-s", "--seed", metavar="seed", default=0,
                            help="Seed used to initialize the weights during "
                                 "training.")
        parsed_args = parser.parse_args(args)
        run_train(parsed_args.model, int(parsed_args.seed),
                  parsed_args.network)

    @staticmethod
    def tune(args):
        # The tuner was used mostly with hardcoded parameters. I started
        # writing some cmd line args but finished tuning the hyperparameters
        # before. No time to clean this stuff now so I will just deactivate it.
        #
        # GOODNIGHT, SWEET PRINCE.

        parser = argparse.ArgumentParser(
            description="Tune the hyperparameters of a model using the "
                        "previously generated data",
            usage=f"{sys.argv[0]} tune [optional args] -m model_dir\n")
        parser.add_argument(metavar="model_dir",
                            help="Folder for the model containing the "
                                 "validate.bin and train.bin generated by the "
                                 "preprocess action.")
        parser.add_argument("-n", "--network",
                            default="cnn", choices=["dense", "lstm", "cnn"],
                            help="Choose which network to use for training.")
        parser.add_argument("-s", "--seed", metavar="seed", default=0,
                            help="Seed used to initialize the weights during "
                                 "tuning.")
        parsed_args = parser.parse_args(args)
        # the function is wrong otherwise I have to import the tuner.py file
        # which in turns requires keras-tuner to be downloaded
        run_train(parsed_args.model, int(parsed_args.seed),
                  parsed_args.network)

    @staticmethod
    def evaluate(args):
        parser = argparse.ArgumentParser(
            description="Run the evaluation on a trained model. This will "
                        "evaluate the confusion matrix with increasing "
                        "number of features.",
            usage=f"{sys.argv[0]} train [optional args] -m model_dir\n")
        parser.add_argument(metavar="model_dir",
                            help="Folder for the model containing the "
                                 "test.bin generated by the preprocess action "
                                 "and the trained model.hd5.")
        parser.add_argument("-o", "--output", metavar="filename",
                            default="output.csv",
                            help="Output file where the test results will be "
                                 "written. The file will be a .csv file.")
        parser.add_argument("-c", "--cut", metavar="max cut", default="0",
                            help="Maximum allowed number of features. 0 for "
                                 "testing all the features.")
        parser.add_argument("-f", "--fixed", metavar="value", default="0",
                            help="Test for a single number of features.")
        parser.add_argument("-s", "--seed", metavar="seed", default="0",
                            help="Seed used to create the sequences.")
        parser.add_argument("-i", "--increment", metavar="cut increment",
                            default="0",
                            help="Increment for each iteration of the "
                                 "evaluator. 0 for exp increment.")
        parsed_args = parser.parse_args(args)
        run_evaluation(parsed_args.model, parsed_args.output,
                       int(parsed_args.cut), int(parsed_args.increment),
                       int(parsed_args.seed), int(parsed_args.fixed))

    @staticmethod
    def summary(args):
        parser = argparse.ArgumentParser(
            description="Prints a summary of the preprocessed dataset.",
            usage=f"{sys.argv[0]} summary [-h] -m model_dir\n")
        parser.add_argument("-m", "--model", metavar="model_dir",
                            required=True,
                            help="Folder for the model containing the "
                                 "files generated by the preprocess action.")
        parsed_args = parser.parse_args(args)
        run_summary(parsed_args.model)


if __name__ == "__main__":
    FlagDetectionTrainer()
