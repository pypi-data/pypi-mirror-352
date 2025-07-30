raise Exception("20241108 No longer needed. Run `pm checksummaries` instead.")
from lino.api import rt
print("compute_project_sums()")
rt.models.ratings.compute_project_sums()
