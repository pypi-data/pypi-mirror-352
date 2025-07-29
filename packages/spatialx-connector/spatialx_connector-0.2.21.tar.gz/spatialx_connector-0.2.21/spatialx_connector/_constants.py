from enum import Enum


V1_API: str = "pyapi/v1"
OPEN_API: str = "openapi"
TOKEN_KEY: str = "SpatialX-Token"
UCC: str = "ucc.go"

# PyAPI
PARSE_DATA_URL: str = "submission/parse_data_information"
RENAME_IMAGE_CHANNELS: str = "elements/rename_image_channels"
SIMPLIFY_SEGMENTATION: str = "elements/simplify_segmentation"

IMPORT_METADATA: str = "metadata/import_metadata"
LIST_DECONVOLUTION_MODELS: str = "query/get_default_deconvolution_models"

# OpenAPI
INFO_URL: str = "account/info"
GROUPS_URL: str = "account/groups"
LIST_URL: str = "directory/entities"
EXTERNAL_MOUNT_URL: str = "mount/external_listing"
LIST_S3: str = "cloud/setting_list"

CREATE_STUDY_URL: str = "study/create"
LIST_STUDY_URL: str = "study/list"
LIST_PUBLIC_STUDY_URL: str = "study/list_public"
DETAIL_STUDY_URL: str = "study/detail"
UPDATE_STUDY_URL: str = "study/update"
DELETE_STUDY_URL: str = "study/stop_create_submit"

CREATE_SAMPLE_URL: str = "sample/create"
LIST_SAMPLE_URL: str = "sample/list"
DETAIL_SAMPLE_URL: str = "sample/detail"
RENAME_SAMPLE_URL: str = "sample/rename"
DELETE_SAMPLE_URL: str = "sample/delete"

DETAIL_SAMPLE_DATA_URL: str = "data/detail"
ADD_SAMPLE_DATA_URL: str = "data/create"
ADD_SAMPLE_DATA_ELEMENT_URL: str = "data/add_element"
RENAME_SAMPLE_DATA_URL: str = "data/rename"
DELETE_SAMPLE_DATA_URL: str = "data/delete"
DELETE_SAMPLE_DATA_ELEMENT_URL: str = "data/delete_element"
ADD_URL: str = "data_extend/add"

UPLOAD_FILE_URL: str = "upload/simple"
UPLOAD_CHUNK_START_URL: str = "upload/chunk/start"
UPLOAD_CHUNK_PROCESS_URL: str = "upload/chunk/process"
UPLOAD_CHUNK_MERGE_URL: str = "upload/chunk/merge"
UPLOAD_CHUNK_FINISH_URL: str = "upload/chunk/finish"
UPLOAD_FOLDER_FINISH_URL: str = "upload/folder_finish"


# Convert from Lens
STUDY_CONVERT_FROM_LENS_URL: str = "study/convert_from_lens"

# Analysis
CREATE_ANALYSIS_URL: str = "analysis/create"
GET_ANNOTATED_ELEMENTS: str = "metadata/get_annotated_element"


# Types
class Technologies(Enum):
    COSMX_VER1 = "COSMX_VER1"
    COSMX_VER2 = "COSMX_VER2"
    MERSCOPE_VER1 = "MERSCOPE_VER1"
    MERSCOPE_VER2 = "MERSCOPE_VER2"
    XENIUM = "XENIUM"
    XENIUM_HE = "XENIUM_HE"

    VISIUM = "VISIUM"
    VISIUM_HD = "VISIUM_HD"
    SLIDE_SEQ = "SLIDE_SEQ"
    VISIUM_HD_TO_SC = "VISIUM_HD_TO_SC"

    SPATIALDATA_ZARR = "SPATIALDATA_ZARR"
    SPATIALDATA_H5AD = "SPATIALDATA_H5AD"
    SPATIALDATA_RDS = "SPATIALDATA_RDS"

    PROTEIN_OME_TIFF = "PROTEIN_OME_TIFF"
    PROTEIN_QPTIFF = "PROTEIN_QPTIFF"
    PROTEIN_MCD = "PROTEIN_MCD"


class SubmissionType(Enum):
    SPATIAL_TRANSCRIPTOMICS = "SUBMIT_SPATIAL_TRANSCRIPTOMICS"
    SPATIAL_BULK = "SUBMIT_SPATIAL_BULK"
    SPATIAL_PROTEOMICS = "SUBMIT_SPATIAL_PROTEOMICS"

    # OTHERS
    PROCESSED_SPATIAL_DATA = "SUBMIT_PROCESSED_SPATIAL_DATA"
    OTHERS_FORMAT_DATA = "SUBMIT_OTHERS_FORMAT_DATA"
    COMBINED_DATASETS = "COMBINED_DATASETS"
    ADDING_ELEMENTS = "ADDING_ELEMENTS"

    @classmethod
    def detect_submission_type(cls, technology: str):
        if technology in [
            Technologies.COSMX_VER1,
            Technologies.COSMX_VER1.value,
            Technologies.COSMX_VER2,
            Technologies.COSMX_VER2.value,
            Technologies.MERSCOPE_VER1,
            Technologies.MERSCOPE_VER1.value,
            Technologies.MERSCOPE_VER2,
            Technologies.MERSCOPE_VER2.value,
            Technologies.XENIUM,
            Technologies.XENIUM.value,
            Technologies.XENIUM_HE,
            Technologies.XENIUM_HE.value,
        ]:
            return cls.SPATIAL_TRANSCRIPTOMICS
        elif technology in [
            Technologies.VISIUM,
            Technologies.VISIUM.value,
            Technologies.VISIUM_HD,
            Technologies.VISIUM_HD.value,
            Technologies.SLIDE_SEQ,
            Technologies.SLIDE_SEQ.value,
        ]:
            return cls.SPATIAL_BULK
        elif technology in [
            Technologies.PROTEIN_OME_TIFF,
            Technologies.PROTEIN_OME_TIFF.value,
            Technologies.PROTEIN_QPTIFF,
            Technologies.PROTEIN_QPTIFF.value,
            Technologies.PROTEIN_MCD,
            Technologies.PROTEIN_MCD.value,
        ]:
            return cls.SPATIAL_PROTEOMICS
        elif technology in [
            Technologies.SPATIALDATA_ZARR,
            Technologies.SPATIALDATA_ZARR.value,
            Technologies.SPATIALDATA_H5AD,
            Technologies.SPATIALDATA_H5AD.value,
            Technologies.SPATIALDATA_RDS,
            Technologies.SPATIALDATA_RDS.value,
        ]:
            return cls.PROCESSED_SPATIAL_DATA
        return cls.OTHERS_FORMAT_DATA


class Species(Enum):
    HUMAN = "human"
    MOUSE = "mouse"
    OTHERS = "others"
    NON_HUMAN_PRIMATE = "nonHumanPrimate"


class StudyType(Enum):
    SINGLECELL_STUDY_TYPE_NUMBER = 0
    SPATIAL_STUDY_TYPE_NUMBER = 1


class StudyStatus(Enum):
    CREATED_STATUS = 0
    SUCCESS_STATUS = 1
    PROCESSING_STATUS = 2
    DELETE_STATUS = 3


class StudyFilter(Enum):
    EQUAL = 0
    NOT_LARGER = 1
    LARGER = 2


class DefaultGroup(Enum):
    PERSONAL_WORKSPACE = "Personal workspace"
    ALL_MEMBERS = "All members"

    LENS_GROUP_ID_PERSONAL_WORKSPACE = "personal"
    LENS_GROUP_ID_ALL_MEMBERS = "all_members"


class ImagesSubmission(Enum):
    # Transcriptomics Technologies
    COSMX_VER1 = "IMAGES_COSMX_VER1"
    COSMX_VER2 = "IMAGES_COSMX_VER2"
    MERSCOPE_VER1 = "IMAGES_MERSCOPE_VER1"
    MERSCOPE_VER2 = "IMAGES_MERSCOPE_VER2"
    XENIUM = "IMAGES_XENIUM"
    XENIUM_HE = "IMAGES_XENIUM_HE"

    # Bulk Technologies
    VISIUM = "IMAGES_VISIUM"
    VISIUM_HD = "IMAGES_VISIUM_HD"

    # Proteomics Technologies
    PROTEIN_OME_TIFF = "IMAGES_PROTEIN_OME_TIFF"  # Lunaphore COMET
    PROTEIN_QPTIFF = "IMAGES_PROTEIN_QPTIFF"  # Akoya PhenoCycler CODEX
    PROTEIN_MCD = "IMAGES_PROTEIN_MCD"  # MCD Public STTARR
    PROTEIN_COSMX_VER2 = "IMAGES_PROTEIN_COSMX_VER2"

    # Processed Data
    ZARR_SPATIALDATA = "IMAGES_ZARR_SPATIALDATA"

    # Specific cases
    TIFFFILE = "IMAGES_TIFFFILE"
    TIFFFILE_3D = "IMAGES_TIFFFILE_3D"
    TIFFFILE_HE = "IMAGES_TIFFFILE_HE"
    FROM_EXISTED = "IMAGES_FROM_EXISTED"
    PROTEIN_FROM_EXISTED = "IMAGES_PROTEIN_FROM_EXISTED"


class SegmentationSubmission(Enum):
    # Transcriptomics Technologies
    COSMX_VER1 = "SEGMENTATION_COSMX_VER1"
    COSMX_VER2 = "SEGMENTATION_COSMX_VER2"
    MERSCOPE_VER1 = "SEGMENTATION_MERSCOPE_VER1"
    MERSCOPE_VER2 = "SEGMENTATION_MERSCOPE_VER2"
    XENIUM = "SEGMENTATION_XENIUM"
    XENIUM_HE = "SEGMENTATION_XENIUM_HE"

    # Bulk Technologies
    VISIUM = "SPOT_VISIUM"
    VISIUM_HD = "SPOT_VISIUM_HD"
    SLIDE_SEQ = "SPOT_SLIDE_SEQ"
    STOMICS_BINS = "SEGMENTATION_STOMICS_BINS"
    STOMICS_CELL_BINS = "SEGMENTATION_STOMICS_CELL_BINS"

    # Processed Data
    ZARR_SPATIALDATA = "SEGMENTATION_ZARR_SPATIALDATA"

    # Specific cases
    PARQUET = "SEGMENTATION_PARQUET"
    GEOJSON = "SEGMENTATION_GEOJSON"
    FEATHER = "SEGMENTATION_FEATHER"
    HALO = "SEGMENTATION_HALO"
    CELL_MASKS = "SEGMENTATION_CELL_MASKS"


class TrasncriptsSubmission(Enum):
    # Transcriptomics Technologies
    COSMX_VER1 = "TRANSCRIPTS_COSMX_VER1"
    COSMX_VER2 = "TRANSCRIPTS_COSMX_VER2"
    MERSCOPE_VER1 = "TRANSCRIPTS_MERSCOPE_VER1"
    MERSCOPE_VER2 = "TRANSCRIPTS_MERSCOPE_VER2"
    XENIUM = "TRANSCRIPTS_XENIUM"
    XENIUM_HE = "TRANSCRIPTS_XENIUM_HE"

    # Processed Data
    ZARR_SPATIALDATA = "TRANSCRIPTS_ZARR_SPATIALDATA"

    # Specific cases
    DATAFRAME = "TRANSCRIPTS_DATAFRAME"


class ExpressionSubmission(Enum):
    IMPORT_ANNDATA = "IMPORT_ANNDATA"

    # Bulk
    VISIUM = "ANNOTATED_DATA_VISIUM"
    VISIUM_HD = "ANNOTATED_DATA_VISIUM_HD"
    SLIDE_SEQ = "ANNOTATED_DATA_SLIDE_SEQ"
    GEOMX = "ANNOTATED_DATA_GEOMX"
    STOMICS_BINS = "ANNOTATED_DATA_STOMICS_BINS"
    STOMICS_CELL_BINS = "ANNOTATED_DATA_STOMICS_CELL_BINS"

    # Processed data
    MERGE_MULTIPLE_ANNDATA = "MERGE_MULTIPLE_ANNDATA"


class CombinedTechnologies(Enum):
    VISIUM = "Visium"
    VISIUM_HD = "Visium HD"
    GEOMX = "GeoMx"
    SINGLE_CELL_TRANSCRIPTOMICS = "Single cell transcriptomics"
    SINGLE_CELL_PROTEOMICS = "Single cell proteomics"


class SubmissionElementKeys(Enum):
    IMAGES = "images"
    PROTEIN_IMAGES = "protein_images"
    SEGMENTATION = "segmentation"
    TRANSCRIPTS = "transcripts"
    CELL_CENTERS = "cell_centers"
    MATRIX = "matrix"
    EXPRESSION = "annotated_data"
    ALIGNMENT = "alignment"
    SCALEFACTORS = "scalefactors"
    TISSUE_POSITIONS = "tissue_positions"
    MPP = "mpp"

    IMAGES_ID = "images_id"
    SEGMENTATION_ID = "segmentation_id"
    SPATIAL_ID = "spatial_id"
    NUCLEI_CHANNELS = "nuclei_channels"
    MEMBRANE_CHANNELS = "membrane_channels"

    REFERENCE_ANNDATA_PATHS = "reference_anndata_paths"
    INCLUDED_IMAGES = "included_images"
    INCLUDED_SEGMENTATION = "included_segmentation"
    METADATA_ACTION = "metadata_action"


class ConnectorKeys(Enum):
    INFORMATION_FIELDS = ["email", "sub_dir", "name", "app_base_url", "routing_table"]

    # Response keys
    ENTITY = "entity"
    ENTITIES = "entities"
    MESSAGE = "message"
    STATUS = "status"
    STUDY = "study"
    SAMPLE = "sample"
    UNIQUE_ID = "unique_id"
    ROOT_FOLDER = "root_folder"

    FILE = "file"
    DIRECTORY = "directory"

    FILES = "files"
    FOLDERS = "folders"
    ARGS = "args"
    KWARGS = "kwargs"
    IDENTITIES = "identities"

    MAP_SUBMIT_RESULT = "map_submit_result"
    ANNOTATED_DATA = "annotated_data"
    TRANSCRIPTS = "transcripts"
    SPOT = "spot"
    MPP = "mpp"

    # Parameter keys
    OBS = "obs"
    OBSM = "obsm"
    BARCODES: str = "barcodes"
    GENES: str = "genes"

    STUDY_PATH = "study_path"
    STUDY_ID = "study_id"
    GROUP_ID = "group_id"
    SPECIES = "species"
    LIMIT = "limit"
    OFFSET = "offset"
    ACTIVE = "active"
    COMPARE = "compare"
    NAME = "name"
    DATA = "data"
    DATA_NAME = "data_name"
    SAMPLE_NAME = "sample_name"
    TITLE = "title"
    KEY = "key"
    VALUE = "value"
    TYPE = "type"
    PATH = "path"
    DATA_PATH = "data_path"
    IGNORE_HIDDEN = "ignore_hidden"
    TECHNOLOGY = "technology"
    SAMPLE_ID = "sample_id"
    SAMPLE_DATA = "sample_data"
    SUBMIT_ID = "submit_id"
    SUBMISSION_NAME = "submission_name"
    SUBMISSION_TYPE = "submission_type"
    SUBMISSION_INFO = "submission_info"
    NEED_DATA = "need_data"
    DATA_ID = "data_id"
    TABLE_ID = "table_id"
    ELEMENT_ID = "element_id"
    LENS_DATA_PATH = "lens_data_path"
    GROUPS = "groups"
    DEFAULT = "default"
    PARAMS = "params"
    DISPLAY_PARAMS = "display_params"
    SUB_TYPE = "sub_type"
    GROUP_TYPE = "group_type"
    DESCRIPTION = "description"
    ELEMENT = "element"
    NEW_NAME = "new_name"
    CLEANUP = "cleanup_flg"
    PUBLICATION = "publication"
    TAGS = "tags"
    AUTHOR = "author"
    ANALYSIS_ID = "analysis_id"

    HTTP_REQ_PERMISISON_NAME_KEY = "permission_name"

    EMAIL_ID = "email_id"
    TOTAL_DATA = "total_data"
    TOTAL_SAMPLE = "total_sample"
    ENABLE_STATUS = "enable_status"

    IMAGES_ID = "images_id"
    SEGMENTATION_ID = "segmentation_id"
    CHANNEL_NAMES = "channel_names"
    TOLERANCE = "tolerance"
    CSV_PATH = "csv_path"

    # Parameter upload keys
    UPLOAD_PARENT_IS_FILE = "parent_is_file"
    UPLOAD_CHUNK_SIZE = "chunk_size"
    UPLOAD_FILE_SIZE = "file_size"
    UPLOAD_OFFSET = "offset"
    UPLOAD_FILE_NAME = "name"
    UPLOAD_FOLDER_NAME = "folder_name"
    UPLOAD_UNIQUE_ID = "unique_id"
    UPLOAD_PATH = "path"
    UPLOAD_MOVE_TO_PARENT = "move_to_parent"
    UPLOAD_SENDING_INDEX = "sending_index"
    UPLOAD_FILE_DATA = "file"
    UPLOAD_TOTAL_CHUNK = "total"
    UPLOAD_IS_CHUNK = "is_chunk"
    UPLOAD_CHUNK_SMALL_SIZE = 1024 * 1024
    UPLOAD_CHUNK_MEDIUM_SIZE = 16 * 1024 * 1024
    UPLOAD_CHUNK_NORMAL_SIZE = 50 * 1024 * 1024
    UPLOAD_CHUNK_LARGE_SIZE = 100 * 1024 * 1024


class NormalizeMethod(Enum):
    RAW = "raw"
    LOG1P_NORMALIZE = "log1p-normalized"
    SQRT_NORMALIZE = "sqrt-normalized"


class SpatialAttrs(Enum):
    IMAGES = "images"
    SHAPES = "shapes"
    POINTS = "points"
    TABLES = "tables"
    LABELS = "labels"

    IMAGES_ELEMENT = "images"
    PROTEIN_IMAGES_ELEMENT = "protein_images"
    IMAGES_ALIGNMENT_ELEMENT = "images_alignment"
    SEGMENTATION_ELEMENT = "segmentation"
    TRANSCRIPTS_ELEMENT = "transcripts"
    CELL_CENTERS_ELEMENT = "cell_centers"
    ANNOTATED_DATA = "annotated_data"
    MULTI_LABELS_ELEMENT = "multi_labels"
    SPOT_ELEMENT = "spot"

    SPATIAL_ELEMENT_MAPPING = {
        IMAGES_ELEMENT: IMAGES,
        PROTEIN_IMAGES_ELEMENT: IMAGES,
        SEGMENTATION_ELEMENT: SHAPES,
        CELL_CENTERS_ELEMENT: POINTS,
        TRANSCRIPTS_ELEMENT: POINTS,
        ANNOTATED_DATA: TABLES,
        SPOT_ELEMENT: SHAPES,
        MULTI_LABELS_ELEMENT: LABELS,
    }

    CHANNELS_KEY = "channels"
    CHANNEL_LABEL = "label"


class EnableStatus(Enum):
    Status_0 = "Created"
    Status_1 = "Ready to use"
    Status_2 = "Processing"
    Status_3 = "Deleted"

    def get_status(status: int):
        res = getattr(EnableStatus, f"Status_{status}")
        if isinstance(res, Enum):
            res = res.value
        return res


class AnnDataAttr(Enum):
    X = "X"
    OBS = "obs"
    VAR = "var"
    OBSM = "obsm"
    VARM = "varm"
    OBSP = "obsp"
    VARP = "varp"


class AnnDataKeys(Enum):
    INDEX_KEY = "_index"


class AnnDataAxis(Enum):
    OBS = 0
    VAR = 1


class USER_ROLE_PERMISSION_HASH2(Enum):
    CREATE_NEW_STUDY = "CREATE_NEW_STUDY"
    MODIFY_STUDY = "MODIFY_STUDY"
    DELETE_STUDY = "DELETE_STUDY"
    SHARE_STUDY_WITH_ANOTHER_GROUP = "SHARE_STUDY_WITH_ANOTHER_GROUP"
    ADD_NEW_METADATA = "ADD_NEW_METADATA"
    MODIFY_METADATA = "MODIFY_METADATA"
    DELETE_METADATA = "DELETE_METADATA"
    STANDARDIZE_METADATA = "STANDARDIZE_METADATA"
    CREATE_NEW_DATABASE = "CREATE_NEW_DATABASE"
    DELETE_DATABASE = "DELETE_DATABASE"
    MODIFY_ONTOLOGIES = "MODIFY_ONTOLOGIES"
    ADD_OR_REMOVE_USERS_IN_GROUP = "ADD_OR_REMOVE_USERS_IN_GROUP"
    CLONE_STUDY_TO_PERSONAL_WORKSPACE = "CLONE_STUDY_TO_PERSONAL_WORKSPACE"
    EXPORT_STUDY = "EXPORT_STUDY"
    ADD_NEW_ANALYSIS = "ADD_NEW_ANALYSIS"
    DELETE_ANALYSIS = "DELETE_ANALYSIS"
    EXPORT_ANALYSIS_RESULT = "EXPORT_ANALYSIS_RESULT"
    ACCESS_PUBLIC_DATASETS = "ACCESS_PUBLIC_DATASETS"
    CHANGE_GROUP_OF_STUDY = "CHANGE_GROUP_OF_STUDY"
    CREATE_NEW_MODELING = "CREATE_NEW_MODELING"
    MODIFY_MODELING = "MODIFY_MODELING"
    DELETE_MODELING = "DELETE_MODELING"
