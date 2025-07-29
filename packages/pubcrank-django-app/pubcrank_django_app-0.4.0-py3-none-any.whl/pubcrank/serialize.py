import pendulum


class DateTimeSerializer:
  @staticmethod
  def from_json(value):
    return pendulum.parse(value)

  @staticmethod
  def to_json(value):
    return value.isoformat()
