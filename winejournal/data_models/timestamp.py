import datetime
import pytz
from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator

from winejournal.extensions import db


class AwareDateTime(TypeDecorator):
    """
    A DateTime type which can only store tz-aware DateTimes.

    Source:
      https://gist.github.com/inklesspen/90b554c864b99340747e
    """
    impl = DateTime(timezone=True)

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            raise ValueError('{!r} must be TZ-aware'.format(value))
        return value

    def __repr__(self):
        return 'AwareDateTime()'


class TimeStampMixin(object):
    # Keep track when records are created and updated.
    time_stamp = datetime.datetime.now(pytz.utc)
    created_on = db.Column(AwareDateTime(),
                           default=time_stamp)
    updated_on = db.Column(AwareDateTime(),
                           default=time_stamp,
                           onupdate=time_stamp)

    def save(self):
        db.session.add(self)
        db.session.commit()

        return self

    def delete(self):
        db.session.delete(self)
        return db.session.commit()

    def __str__(self):
        """
        Create a human readable version of a class instance.

        :return: self
        """
        obj_id = hex(id(self))
        columns = self.__table__.c.keys()

        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in columns)
        return '<%s %s(%s)>' % (obj_id, self.__class__.__name__, values)
