import requests
import json
import csv
import collections

url_repo = 'https://api.github.com/repos/{}/{}'
url_contributors = url_repo + '/contributors'
RepoStats = collections.namedtuple('RepoStats', 
	'contributors, stars, forks, subscribers')
repos = [
	('tensorflow', 'tensorflow'),
	('microsoft', 'cntk'),
	('theano', 'theano'),
	('bvlc', 'caffe'),
	('fchollet', 'keras'),
	('dnouri', 'nolearn'),
	('dmlc', 'mxnet'),
	('lasagne', 'lasagne'),
	('torch', 'torch7')
]

stats = dict()

params = {'per_page': 100}

for repo in repos:
	print 'Fetching {}/{}'.format(repo[0], repo[1])
	r = requests.get(url_repo.format(repo[0], repo[1]), params=params)	
	if (r.ok):
		repo_info = json.loads(r.text or r.content)
		stars = repo_info['stargazers_count']
		forks = repo_info['forks_count']
		subscribers = repo_info['subscribers_count']
	else:
		print 'Warning: failed to get {}/{}'.format(repo[0], repo[1])
		continue
	contributors = 0
	r = requests.get(url_contributors.format(repo[0], repo[1]), params=params)
	if (r.ok):
		repo_contributors = json.loads(r.text or r.content)
		contributors += len(repo_contributors)
		next_link = r.links.get('next', None)
		while next_link is not None:
			r = requests.get(next_link['url'], params=params)
			repo_contributors = json.loads(r.text or r.content)
			contributors += len(repo_contributors)
			next_link = r.links.get('next', None)
	stats[repo[1]] = RepoStats(contributors=contributors, 
							   stars=stars, 
							   forks=forks, 
							   subscribers=subscribers)

out_path = 'dl_stats.csv'

print 'Saving output to {}'.format(out_path)
with open(out_path, 'wb') as f:
	writer = csv.writer(f, delimiter=',')
	writer.writerow(['Library', 'Contributors', 'Stars', 'Forks', 'Subscribers'])
	for repo in stats:
		writer.writerow([repo, 
						 stats[repo].contributors, 
						 stats[repo].stars,
						 stats[repo].forks,
						 stats[repo].subscribers
						 ])

print 'Done'
