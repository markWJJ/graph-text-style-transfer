"""Config
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# pylint: disable=invalid-name

import copy
import texar as tx

# pretrain_nepochs = 10 # Number of pre-train epochs (training as autoencoder)
# fulltrain_nepochs = 3
# max_nepochs = pretrain_nepochs + fulltrain_nepochs # Total number of training epochs (including pre-train and full-train)

display = 500  # Display the training results every N training steps.
display_eval = 1e10 # Display the dev results every N training steps (set to a
                    # very large value to disable it).
restore = ''   # Model snapshot to restore from

model_name = 'GTAE'

# lambda_t_graph = 0.05    # Weight of the graph classification loss
# lambda_t_sentence = 0.02 # Weight of the sentence classification loss
gamma_decay = 0.5 # Gumbel-softmax temperature anneal rate

max_sequence_length = 15 # Maximum number of tokens in a sentence

train_data = {
    'batch_size': 64,
    'seed': 666,
    'datasets': [
        {
            'files': './data/political/political.train.text',
            'vocab_file': './data/political/vocab_political',
            'data_name': ''
        },
        {
            'files': './data/political/political.train.labels',
            'data_type': 'int',
            'data_name': 'labels'
        },
        {
            'files': './data/political/political.train_adjs.tfrecords',
            'data_type': 'tf_record',
            'numpy_options': {
                'numpy_ndarray_name': 'adjs',
                'shape': [max_sequence_length + 2, max_sequence_length + 2],
                'dtype': 'tf.int32'
            },
            'feature_original_types':{
                'adjs':['tf.string', 'FixedLenFeature']
            }
        }
        # {
        #     'files': './data/political/political.train_identities.tfrecords',
        #     'data_type': 'tf_record',
        #     'numpy_options': {
        #         'numpy_ndarray_name': 'identities',
        #         'shape': [max_sequence_length + 2, max_sequence_length + 2],
        #         'dtype': 'tf.int32'
        #     },
        #     'feature_original_types':{
        #         'identities':['tf.string', 'FixedLenFeature']
        #     }
        # }
    ],
    'name': 'train'
}

val_data = copy.deepcopy(train_data)
val_data['datasets'][0]['files'] = './data/political/political.dev.text'
val_data['datasets'][1]['files'] = './data/political/political.dev.labels'
val_data['datasets'][2]['files'] = './data/political/political.dev_adjs.tfrecords'
# val_data['datasets'][3]['files'] = './data/political/political.dev_identities.tfrecords'

test_data = copy.deepcopy(train_data)
test_data['datasets'][0]['files'] = './data/political/political.test.text'
test_data['datasets'][1]['files'] = './data/political/political.test.labels'
test_data['datasets'][2]['files'] = './data/political/political.test_adjs.tfrecords'
# test_data['datasets'][3]['files'] = './data/political/political.test_identities.tfrecords'

dim_hidden = 512
model = {
    'dim_c': dim_hidden,
    'embedder': {
        'dim': dim_hidden,
    },
    'encoder': {
        'num_blocks': 2,
        'dim': dim_hidden,
        'use_bert_config': False,
        'embedding_dropout': 0.1,
        'residual_dropout': 0.1,
        'graph_multihead_attention': {
            'name': 'multihead_attention',
            'num_units': dim_hidden,
            'output_dim': dim_hidden,
            'num_heads': 8,
            'dropout_rate': 0.1,
            'output_dim': dim_hidden,
            'use_bias': False,
        },
        'initializer': None,
        'name': 'graph_transformer_encoder',
    },
    'rephrase_encoder': {
        'rnn_cell': {
            'type': 'GRUCell',
            'kwargs': {
                'num_units': dim_hidden
            },
            'dropout': {
                'input_keep_prob': 0.5
            }
        }
    },
    'rephrase_decoder': {
        'rnn_cell': {
            'type': 'GRUCell',
            'kwargs': {
                'num_units': dim_hidden,
            },
            'dropout': {
                'input_keep_prob': 0.5,
                'output_keep_prob': 0.5
            },
        },
        'attention': {
            'type': 'DynamicBahdanauAttention',
            'kwargs': {
                'num_units': dim_hidden,
            },
            'attention_layer_size': dim_hidden,
        },
        'max_decoding_length_train': 21,
        'max_decoding_length_infer': 20,
    },
    'classifier': {
        'kernel_size': [3, 4, 5],
        'filters': 128,
        'other_conv_kwargs': {'padding': 'same'},
        'dropout_conv': [1],
        'dropout_rate': 0.5,
        'num_dense_layers': 0,
        'num_classes': 1
    },
    'opt': {
        'optimizer': {
            'type':  'AdamOptimizer',
            'kwargs': {
                'learning_rate': 5e-4,
            },
        },
    },
}
