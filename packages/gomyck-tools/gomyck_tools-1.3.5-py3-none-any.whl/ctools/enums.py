def value_of(e, v):
  for member_name, member in e.__members__.items():
    if member.value == v:
      return member
