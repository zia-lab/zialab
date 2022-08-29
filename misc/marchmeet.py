from ics import Calendar, Event
import pickle, re, requests
import pandas as pd
import datetime

def regsearch(string, keyword):
    if re.match(r'.*\b({0})\b.*'.format(keyword),string,flags=re.IGNORECASE):
        return True
    else:
        return False
def abstract_search(abstract, keywordlist):
    matches = [regsearch(abstract, keyw) for keyw in keywordlist]
    return all(matches)
nice_keys = ['title','date','authors','presenter','abstract','room',
             'time_interval','live_links','duration_in_min']
def make_calendar(search_type, keywords, march_meeting_df):
  '''This function searches for talks in the 2021 March Meeting.
  It creates a .md markdown file with the search results, and an .ics calendar
  file with the events back to back, starting from the current time.
  Files are saved in the volatile memory of the runtime.

  Examples:
    make_calendar('abstract',['europium','red to orange'], march_meeting_df)
    -- searches for talks about europium that also contain 'red to orange'
    make_calendar('html' , 'Brown University', march_meeting_df)
    -- searches for talks that contain '(Brown University)' in the html of
       all the talks.
  
  Args:
    search_type (str): either 'html' or 'abstract'
    keywords    (...): if search_type 'html' then a single string 
                       if search_type is 'abstracts' then a list of strings.
    march_meeting_df (pd.Dataframe): the Dataframe with all the data
  Returns:
    pd.Dataframe     : the search results

  '''
  the_time = datetime.datetime.now() - datetime.timedelta(hours=4)
  all_abstracts = []
  assert search_type in ['html','abstract'], "seach type should be either abstract or html"
  if search_type == 'abstract':
    assert type(keywords) == list, 'keywords must be a list of strings'
  else:
    assert type(keywords) == str, 'keywords must be a single string'
  if search_type == 'html':
    results_suffix = keywords
    results_suffix = results_suffix.replace(' ','-')
    if "\)" in keywords:
        results_suffix.replace("\)","")
    results_file = 'all-abstracts-%s.md' % results_suffix
  else:
    results_suffix = keywords[0]+'-and-others'
    results_suffix = results_suffix.replace(' ','-')
    results_file = 'all-abstracts-%s.md' % results_suffix
  if search_type == 'html':
    good_talks = march_meeting_df['html'].str.contains(keywords, case=False)
    good_talks = march_meeting_df[good_talks]
    good_ones = ((~ good_talks['not_participating'])
                & (good_talks['date'] != 'TBD')
                & (~(good_talks['presenter'] == ''))
                & (~pd.isnull(good_talks['time_interval'])))
    good_talks = good_talks[good_ones]
  else:
    good_talks = march_meeting_df['abstract'].apply(lambda x: abstract_search(x,keywords))
    good_talks = march_meeting_df[good_talks]
    good_ones = ((~ good_talks['not_participating'])
                & (good_talks['date'] != 'TBD')
                & (~(good_talks['presenter'] == ''))
                & (~pd.isnull(good_talks['time_interval'])))
    good_talks = good_talks[good_ones]
  all_good_talks = []
  for talk in good_talks.iterrows():
      talk = talk[1]
      if talk['presenter']:
          all_good_talks.append({k: talk[k] for k in talk if k in nice_keys})
          if len(talk['authors'])>1:
              all_abstracts.append('## %s\n\n*%s*\n\n(%s)\n\n%s\n%s' % (talk['title'],
                  talk['presenter'],'; '.join(talk['authors']),talk['abstract'],talk['live_links']))
          else:
              all_abstracts.append('## %s\n\n*%s*\n\n%s\n' % (talk['title'],
                                        talk['presenter'],talk['abstract']))
  all_abstracts_doc = '\n'.join(all_abstracts)
  all_abstracts_doc = '\n'.join(all_abstracts)
  open(results_file,'w').write(all_abstracts_doc)
  print("Saving results file to %s ..." % results_file)

  print("Creating Calendar ...")
  parsed_times = []
  c = Calendar()
  parsed_titles = []
  for good_talk in good_talks.iterrows():
      good_talk = good_talk[1]
      try:
          e = Event()
          if good_talk['authors'] and (len(good_talk['authors'])>1):
              parsed_event_name = ('%s - %s (%s)') % (good_talk['presenter'],
                            good_talk['title'],'; '.join(good_talk['authors']))
          else:
              parsed_event_name = ('%s - %s ') % (good_talk['presenter'], good_talk['title'])
          if 'time_interval' not in good_talk.keys():
              continue
          if parsed_event_name not in parsed_titles:
              parsed_titles.append(parsed_event_name)
              e.name = parsed_event_name
              e.url = good_talk['live_links']
              time_interval = good_talk['time_interval']
              parsed_date = good_talk['date'].strftime('%Y-%m-%d')
              start_time = time_interval[0]
              start_hour = int(start_time.split(':')[0]) + 5
              start_min = (start_time.split(':')[1].split()[0])
              if 'PM' in start_time:
                  start_hour += 12
              if start_hour > 23:
                  start_hour -= 12
              start_hour, start_min = str(start_hour).zfill(2), start_min.zfill(2)
              end_time = time_interval[1]
              end_hour = int(end_time.split(':')[0])  + 5
              end_min = (end_time.split(':')[1].split()[0])
              if 'PM' in start_time:
                  end_hour += 12
              if end_hour > 23:
                  end_hour -= 12
              end_hour = str(end_hour).zfill(2)
              end_min = end_min.zfill(2)
              full_start_time_parsed = '%sT%s:%s:00' % (parsed_date, start_hour, start_min)
              full_end_time_parsed = '%sT%s:%s:00' % (parsed_date, end_hour, end_min)
              parsed_times.append([full_start_time_parsed, full_end_time_parsed])
              full_start_time_parsed = (the_time+datetime.timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M')
              the_end_time = the_time + datetime.timedelta(minutes=good_talk['duration_in_min'])
              full_end_time_parsed = (the_end_time+datetime.timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M') 
              e.begin = full_start_time_parsed
              e.end = full_end_time_parsed
              e.description = good_talk['abstract']
              c.events.add(e)
              the_time = the_end_time + datetime.timedelta(minutes=5)
      except:
          pass
  print('Total events = %d' % len(parsed_titles))
  with open('march-meeting-%s.ics' % results_suffix, 'w') as f:
      f.writelines(c)
  print("Saving calendar to %s " % ('march-meeting-%s.ics' % results_suffix))
  print("Done!")
  return good_talks