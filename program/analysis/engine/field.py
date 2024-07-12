"""
Fields used by restful api.
"""

from flask_restful import fields

CLASSIFICATION_FIELD = {
    'resource_limit': fields.String,
    'workload_type': fields.String,
    'percentage': fields.Float,
}

CLASSIFICATION_POST_FIELD = fields.Nested(CLASSIFICATION_FIELD)