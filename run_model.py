import argparse
import logging

import joblib
import yaml
import pandas as pd
import numpy as np

import src.model as model

logging.basicConfig(format='%(name)-12s %(levelname)-8s %(message)s', level=logging.DEBUG)
logger = logging.getLogger('AVC-project-modelling')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Model pipeline for project")

    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for getting data
    sp_get = subparsers.add_parser("get", description="get data")
    sp_get.add_argument("--input", help="input file path")
    sp_get.add_argument('--config', default='config/config.yaml', help='Path to configuration file')
    sp_get.add_argument('--output', help='Output file path')

    # Sub-parser for clean data
    sp_clean = subparsers.add_parser("clean", description="get features")
    sp_clean.add_argument("--input", help="input file path")
    sp_clean.add_argument('--config', default='config/config.yaml', help='Path to configuration file')
    sp_clean.add_argument('--output', help='Output file path')

    # Sub-parser for splitting data
    sp_split = subparsers.add_parser("split", description="split data")
    sp_split.add_argument("--input", help="input file path")
    sp_split.add_argument('--config', default='config/config.yaml', help='Path to configuration file')
    sp_split.add_argument('--output', nargs='+', help='Output file path')

    # Sub-parser for training model
    sp_train = subparsers.add_parser("train", description="train model")
    sp_train.add_argument("--input", nargs='+', help="input file path")
    sp_train.add_argument('--config', default='config/config.yaml', help='Path to configuration file')
    sp_train.add_argument('--output', help='Output file path')

    # Sub-parser for scoring model
    sp_score = subparsers.add_parser("score", description="score model")
    sp_score.add_argument("--input", nargs='+', help="input file path")
    sp_score.add_argument('--config', default='config/config.yaml', help='Path to configuration file')
    sp_score.add_argument('--output', nargs='+', help='Output file path')

    # Sub-parser for evaluating model
    sp_evaluate = subparsers.add_parser("evaluate", description="evaluate model")
    sp_evaluate.add_argument("--input", nargs='+', help="input file path")
    sp_evaluate.add_argument('--config', default='config/config.yaml', help='Path to configuration file')
    sp_evaluate.add_argument('--output', help='Output file path')

    args = parser.parse_args()
    sp_used = args.subparser_name

    # load configuration file
    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    logger.info('Configuration file loaded')

    inputs = []
    if sp_used == 'get':
        output = model.get_data(**config['model']['get_data'])
        output.to_csv(args.output, index=False)
        logger.info('data saved to %s', args.output)

    elif sp_used == 'clean':
        try:
            ingest = pd.read_csv(args.input)
            logger.debug('data loaded')
        except FileNotFoundError:
            logger.error('File not found at path %s', args.input)
        except pd.errors.EmptyDataError:
            logger.error('No data')
        except pd.errors.ParserError:
            logger.error('Parse error')
        output = model.clean_data(ingest, **config['model']['clean_data'])
        output.to_csv(args.output, index=False)
        logger.info('processed data saved to %s', args.output)

    elif sp_used == 'split':
        try:
            ingest = pd.read_csv(args.input)
            logger.debug('data loaded')
        except FileNotFoundError:
            logger.error('File not found at path %s', args.input[0])
        except pd.errors.EmptyDataError:
            logger.error('No data')
        except pd.errors.ParserError:
            logger.error('Parse error')
        output = model.split_data(ingest, **config['model']['split_data'])
        output[0].to_csv(args.output[0], index=False)
        logger.info('X_train saved to %s', args.output[0])
        output[1].to_csv(args.output[1], index=False)
        logger.info('X_test saved to %s', args.output[1])
        output[2].to_pickle(args.output[2])
        logger.info('y_train saved to %s', args.output[2])
        output[3].to_pickle(args.output[3])
        logger.info('y_test saved to %s', args.output[3])

    elif sp_used == 'train':
        try:
            ingest1 = pd.read_csv(args.input[0])
            logger.debug('data loaded')
        except FileNotFoundError:
            logger.error('File not found at path %s', args.input)
        except pd.errors.EmptyDataError:
            logger.error('No data')
        except pd.errors.ParserError:
            logger.error('Parse error')

        ingest2 = pd.read_pickle(args.input[1])
        output = model.train_model(ingest1, ingest2, **config['model']['train_model'])
        joblib.dump(output, args.output)
        logger.info('random forest model saved to %s', args.output)

    elif sp_used == 'score':
        try:
            ingest1 = joblib.load(args.input[0])
            logger.info('Loaded model from %s', args.input[0])
        except OSError:
            logger.error('Model is not found from %s', args.input[0])
        try:
            ingest2 = pd.read_csv(args.input[1])
            logger.debug('data loaded')
        except FileNotFoundError:
            logger.error('File not found at path %s', args.input[1])
        except pd.errors.EmptyDataError:
            logger.error('No data')
        except pd.errors.ParserError:
            logger.error('Parse error')

        output = model.predict(ingest1, ingest2)

        np.save(args.output[0], output[0])
        logger.info('predicted probability saved to %s', args.output[0])
        np.save(args.output[1], output[1])
        logger.info('predicted label saved to %s', args.output[1])

    elif sp_used == 'evaluate':
        ingest1 = pd.read_pickle(args.input[0])

        with open(args.input[1], 'rb') as f:
            ingest2 = np.load(f)
        with open(args.input[2], 'rb') as f:
            ingest3 = np.load(f)
        output = model.evaluation(ingest1, ingest2, ingest3)
        output.to_csv(args.output)
        logger.info('confusion matrix saved to %s', args.output)
