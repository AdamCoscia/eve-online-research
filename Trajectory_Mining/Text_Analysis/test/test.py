import os
for root, dirs, files in os.walk("../Killmail_Fetching/killmail_scrapes/byregion", topdown=False):
	for name in sorted(files):
		print(os.path.join(root, name))
