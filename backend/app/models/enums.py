import enum


class UserRole(str, enum.Enum):
    admin    = "admin"
    ngo_user = "ngo_user"


class ChannelType(str, enum.Enum):
    whatsapp = "whatsapp"
    sms      = "sms"


class NotificationStatus(str, enum.Enum):
    sent      = "sent"
    delivered = "delivered"
    failed    = "failed"
    retrying  = "retrying"


class CommandType(str, enum.Enum):
    REG     = "REG"
    STOP    = "STOP"
    STATUS  = "STATUS"
    UNKNOWN = "UNKNOWN"
