import os
import datetime
import csv
import urllib.request
import requests

credentials = 'username', 'password'
zendesk = 'https://<subdomain>.zendesk.com'
language = 'en-US'

date = datetime.date.today()

#backup_path = os.path.join(str(date), language)
#if not os.path.exists(backup_path):
#	os.makedirs(backup_path)

log = []

pageNum = 53000
endpoint = zendesk + '/api/v2/tickets/1'

def funcA(endpoint, pageNum):
	print('funcA')
	print(endpoint)
	next = endpoint
	
#	backup_path = os.path.join('Tickets', str(pageNum))
#	if not os.path.exists(backup_path):
#		os.makedirs(backup_path)

	while endpoint != 0:
		response = requests.get(endpoint, auth=credentials)
		if response.status_code != 200 and response.status_code != 404:
			print('Failed to retrieve tickets with error {}'.format(response.status_code))
			exit()
		data = response.json()

		if data.get('ticket') is None:
			endpoint = 0
			print('-----SKIPPED-----')
		else:
			backup_path = os.path.join('TicketsExport', str(pageNum))
			if not os.path.exists(backup_path):
				os.makedirs(backup_path)
				
			if data['ticket']['subject'] is None: # If Subject is NULL
				subject = '<h1> Review Ticket </h1>'
			else:
				subject = '<h1>' + data['ticket']['subject'] + '</h1>'
			dateCreated = '<h3>' + data['ticket']['created_at'] + '</h3>'
			print(subject)
			filename = '{id}.html'.format(id=data['ticket']['id'])
			print(next)
			
			# Comments
			
			endpoint2 = next + '/comments.json'
			response2 = requests.get(endpoint2, auth=credentials)
			if response2.status_code != 200:
				print('Failed to retrieve ticket with error {}'.format(response.status_code))
				exit()
			data2 = response2.json()

			with open(os.path.join(backup_path, filename), mode='w', encoding='utf-8') as f:
				f.write(subject + '\n' + dateCreated + '\n' + '\n' + data['ticket']['description'])


			type = 'true'
			for comment in data2['comments']:
				if comment['html_body'] is None:
					continue
				if comment['public'] == True:
					type = '<br><h3> ----- Email ----- <h3>'
				else:
					type = '<br><h3> ----- Comment ----- <h3>'
				
				commentCreated = comment['created_at']
				
				if comment.get('via').get('source').get('from').get('address') is None:
					emailFrom = ''
				else:
					emailFrom = comment['via']['source']['from']['address']
				if comment.get('via').get('source').get('from').get('name') is None:
					emailName = ''
				else:
					emailName = comment['via']['source']['from']['name']
				body = comment['html_body']
				
				print(emailName + ' - ' + emailFrom) 
				
				with open(os.path.join(backup_path, filename), mode='a+', encoding='utf-8') as f:
					f.write('\n' + type + '\n' + commentCreated + '\n' + emailName + ' - ' + emailFrom + '\n' + body)		


				# Attachments

				class AppURLopener(urllib.request.FancyURLopener):
					version = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.69 Safari/537.36"
				urllib._urlopener = AppURLopener()

				for attachment in comment['attachments']:
					endpoint3 = attachment['url']
					response3 = requests.get(endpoint3, auth=credentials)
					if response3.status_code != 200:
						print('Failed to retrieve ticket with error {}'.format(response.status_code))
						exit()
					data3 = response3.json()
				
					urllib._urlopener.retrieve(attachment['content_url'], os.path.join(backup_path, attachment['file_name']))
					
				
				print('{id} copied!'.format(id=data['ticket']['id']))


				log.append((filename, data['ticket']['subject'], data['ticket']['id']))
			endpoint = 0
	
	funcB(pageNum)


def funcB(pageNum):
	print('funcB')
	pageNum = pageNum + 1
	ndpnt = zendesk + '/api/v2/tickets/' + str(pageNum)
	print(ndpnt)
	funcA(ndpnt, pageNum)


def funcAA():
	print('funcAA')
	ndpnt = zendesk + '/api/v2/tickets.json?start_time=1262304000&page=' + str(pageNum)
	funcA(ndpnt)



funcB(pageNum)

print(endpoint)




