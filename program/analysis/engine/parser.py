from flask_restful import reqparse

OPTIMIZER_POST_PARSER = reqparse.RequestParser()
OPTIMIZER_POST_PARSER.add_argument('max_eval', type=int, required=True,
                                   help="max_eval cannot be null")
OPTIMIZER_POST_PARSER.add_argument('knobs', type=list, location='json',
                                   help="knobs list cannot be null")
OPTIMIZER_POST_PARSER.add_argument('engine',
                                   choices=('random', 'forest', 'gbrt', 'extraTrees',
                                            'abtest', 'gridsearch'),
                                   help='engine choice: {error_msg}')
OPTIMIZER_POST_PARSER.add_argument('history_path', type=list, location='json',
                                   help='path to load tuning history')
OPTIMIZER_POST_PARSER.add_argument('random_starts', type=int, location='json',
                                   help="random_starts cannot be null")
OPTIMIZER_POST_PARSER.add_argument('x_ref', type=list, location='json',
                                   help="the reference of x0 list")
OPTIMIZER_POST_PARSER.add_argument('y_ref', type=list, location='json',
                                   help="the reference of y0 list")
OPTIMIZER_POST_PARSER.add_argument('sel_feature', type=bool, location='json',
                                   help="enable the feature selection or not")
OPTIMIZER_POST_PARSER.add_argument('split_count', type=int, location='json',
                                   help="split_count cannot be null")
OPTIMIZER_POST_PARSER.add_argument('noise', type=float, location='json',
                                   help="the noise can not be null")
OPTIMIZER_POST_PARSER.add_argument('prj_name', type=str, location='json',
                                   help="prj_name cannot be null")
OPTIMIZER_POST_PARSER.add_argument('feature_selector', choices=('wefs', 'vrfs'),
                                   help="importance feature selector: {error_msg}")

OPTIMIZER_PUT_PARSER = reqparse.RequestParser()
OPTIMIZER_PUT_PARSER.add_argument('iterations', type=int, required=True,
                                  help="iterations cannot be null")
OPTIMIZER_PUT_PARSER.add_argument('value', type=str, required=True,
                                  help="value cannot be null")
OPTIMIZER_PUT_PARSER.add_argument('line', type=str, required=True,
                                  help="line cannot be null")
OPTIMIZER_PUT_PARSER.add_argument('prj_name', type=str, required=True,
                                  help="project name cannot be null")
OPTIMIZER_PUT_PARSER.add_argument('max_iter', type=int, required=True,
                                  help="max iterations cannot be null")


CLASSIFICATION_POST_PARSER = reqparse.RequestParser()
CLASSIFICATION_POST_PARSER.add_argument('modelpath', required=True,
                                        help="The modelfile to be used")
CLASSIFICATION_POST_PARSER.add_argument('data',
                                        help="The data path to be used")
CLASSIFICATION_POST_PARSER.add_argument('model',
                                        help="The model self trained to be used")

TRAIN_POST_PARSER = reqparse.RequestParser()
TRAIN_POST_PARSER.add_argument('datapath', required=True,
                               help="The datapath can not be null")
TRAIN_POST_PARSER.add_argument('modelname', required=True,
                               help="The model name can not be null")
TRAIN_POST_PARSER.add_argument('modelpath', required=True,
                               help="The model path can not be null")

DETECT_POST_PARSER = reqparse.RequestParser()
DETECT_POST_PARSER.add_argument('appname', required=True, help="The appname path can not be null")
DETECT_POST_PARSER.add_argument('detectpath', type=str, help="The path of file to be detect")

TRANSFER_PUT_PARSER = reqparse.RequestParser()
TRANSFER_PUT_PARSER.add_argument('type', type=str, required=True,
                                 help="type of data can not be null")
TRANSFER_PUT_PARSER.add_argument('collect_id', type=int, required=True,
                                 help="Collection id can not be null")
TRANSFER_PUT_PARSER.add_argument('status', type=str, required=True, help="Status can not be null")
TRANSFER_PUT_PARSER.add_argument('collect_data', type=str, required=False, help="Collection data")
TRANSFER_PUT_PARSER.add_argument('workload_type', type=str, required=False, help="Workload type")