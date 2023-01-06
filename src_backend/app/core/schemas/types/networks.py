from pydantic import constr

from app.core.schemas.regexes import networks as network_regexes

Host = constr(min_length=4, max_length=1000, regex=network_regexes.host_regex)
