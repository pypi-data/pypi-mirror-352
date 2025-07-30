from enum import Enum

class TimeFreshness(Enum):  
    NO_LIMIT = "noLimit"
    ONE_DAY = "oneDay"
    ONE_WEEK = "oneWeek" 
    ONE_MONTH = "oneMonth"
    ONE_YEAR = "oneYear"