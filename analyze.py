import pandas as pd
import numpy as np
import re

pd.options.display.max_rows = 50

def analyze_election(file, year):
    print "ELECTION YEAR ", year
    df = pd.read_csv('input/' + file)
    if year=='2010':
        df = df[['STATE ABBREVIATION', 'STATE', 'DISTRICT',  'CANDIDATE NAME (First)', 'CANDIDATE NAME (Last)', 'PARTY', 'GENERAL ', 'GENERAL %','COMBINED GE PARTY TOTALS (CT, NY, SC)','COMBINED % (CT, NY, SC)']].dropna(subset=['CANDIDATE NAME (Last)']).rename(columns = {'GENERAL ':'GENERAL VOTES', 'DISTRICT':'D'})
        df['GE WINNER INDICATOR'] = ''
    elif year=='2008':
        df = df[['STATE ABBREVIATION', 'STATE', 'DISTRICT',  'CANDIDATE NAME (First)', 'Candidate Name (Last)', 'PARTY', 'GENERAL ', 'GENERAL %','COMBINED GE PARTY TOTALS (CT, NY)','COMBINED % (CT, NY)']].dropna(subset=['Candidate Name (Last)'])
        df = df.rename(columns = {'GENERAL ':'GENERAL VOTES', 'DISTRICT':'D','COMBINED GE PARTY TOTALS (CT, NY)':'COMBINED GE PARTY TOTALS (CT, NY, SC)','COMBINED % (CT, NY)':'COMBINED % (CT, NY, SC)', 'Candidate Name (Last)':'CANDIDATE NAME (Last)'})
        df['GE WINNER INDICATOR'] = ''
    elif year=='2006':
        df = df[['STATE ABBREVIATION', 'STATE', 'DISTRICT',  'FIRST NAME', 'LAST NAME', 'PARTY', 'GENERAL', 'GENERAL %','COMBINED GE PARTY TOTALS (NY, SC)','COMBINED % (NY, SC)']].dropna(subset=['LAST NAME'])
        df = df.rename(columns = {'GENERAL':'GENERAL VOTES', 'DISTRICT':'D','COMBINED GE PARTY TOTALS (NY, SC)':'COMBINED GE PARTY TOTALS (CT, NY, SC)','COMBINED % (NY, SC)':'COMBINED % (CT, NY, SC)', 'LAST NAME':'CANDIDATE NAME (Last)', 'FIRST NAME':'CANDIDATE NAME (First)'})
        df['GE WINNER INDICATOR'] = ''
    elif year=='2004':
        df = df[['STATE ABBREVIATION', 'STATE', 'DISTRICT',  'FIRST NAME', 'LAST NAME', 'PARTY', 'GENERAL', 'GENERAL %']].dropna(subset=['LAST NAME'])
        df = df.rename(columns = {'GENERAL':'GENERAL VOTES', 'DISTRICT':'D', 'LAST NAME':'CANDIDATE NAME (Last)', 'FIRST NAME':'CANDIDATE NAME (First)'})
        df['GE WINNER INDICATOR'] = ''
    elif year=='2002':
        df = df[['STATE', 'DISTRICT',  'FIRST NAME', 'LAST NAME', 'PARTY', 'GENERAL RESULTS', 'GENERAL %']].dropna(subset=['LAST NAME'])
        df = df.rename(columns = {'GENERAL RESULTS':'GENERAL VOTES', 'DISTRICT':'D', 'LAST NAME':'CANDIDATE NAME (Last)', 'FIRST NAME':'CANDIDATE NAME (First)'})
        df['STATE ABBREVIATION'] = df['STATE'].str.strip()
        df['GE WINNER INDICATOR'] = ''
    else:
        df = df[['STATE ABBREVIATION', 'STATE', 'D',  'CANDIDATE NAME (First)', 'CANDIDATE NAME (Last)', 'PARTY', 'GENERAL VOTES ', 'GENERAL %', 'GE WINNER INDICATOR','COMBINED GE PARTY TOTALS (CT, NY, SC)','COMBINED % (CT, NY, SC)']].dropna(subset=['CANDIDATE NAME (Last)']).rename(columns = {'GENERAL VOTES ':'GENERAL VOTES'})
    # Substitute correct totals for the weird elections
    if year!='2004' and year!='2002':
        df.loc[df['COMBINED GE PARTY TOTALS (CT, NY, SC)'].notnull(),'GENERAL VOTES'] = df['COMBINED GE PARTY TOTALS (CT, NY, SC)']
        df.loc[df['COMBINED % (CT, NY, SC)'].notnull(),'GENERAL %'] = df['COMBINED % (CT, NY, SC)']
    df.loc[df['GENERAL VOTES']=='Unopposed','GENERAL %'] = "100%"
    df['GENERAL VOTES'] = df['GENERAL VOTES'].str.replace('Unopposed',"0")
    df['GE WINNER INDICATOR'] = df['GE WINNER INDICATOR'].replace('W (Runoff)','W')
    df = df.loc[df['GENERAL %'].notnull()]
    df['GENERAL VOTES'] = df['GENERAL VOTES'].str.replace(',','').str.replace('#','').str.replace('n/a','').str.replace('  ','').str.replace('?','').str.replace('Withdrew -- after primary?','')
    df['GENERAL %'] = df['GENERAL %'].str.replace('%','').str.replace('n/a',"").str.replace('\t','')
    df = df[np.logical_not(df['D'].str.contains('S',case=True))]
    df = df[np.logical_not(df['D'].str.contains('UNEXPIRED',case=True))]
    df['D'] = df['D'].str.replace(' - FULL TERM','')
    # Rename major party affiliates
    df['PARTY'] = df['PARTY'].str[0]
    # Keep only major parties and States with voting members
    if year=="2012":
        df['GE WINNER INDICATOR'] = df['GE WINNER INDICATOR'].str.replace("WW","W")
    if year=="2014":
        df.loc[df['CANDIDATE NAME (Last)'].isin(['Huelskamp','Jenkins','Yoder']),'PARTY'] = "R" #UGHHH
    if year=="2002":
        df.loc[df['CANDIDATE NAME (First)']=='Bernie ','PARTY'] = "D"
    df = df[df['PARTY'].isin(['D','R'])]
    df = df.drop_duplicates(['STATE', 'D',  'CANDIDATE NAME (First)', 'CANDIDATE NAME (Last)', 'PARTY'])
    df = df[np.logical_not(df['STATE'].isin(['Guam','District of Columbia','American Samoa','Virgin Islands','Northern Mariana Islands','Puerto Rico','District of Columbi','DC','GU','VI','AS']))]
    df['year'] = year
    if year=='2002': df = df[np.logical_not(df['GENERAL VOTES'].str.contains('[',regex=False))]
    if year=="2002":
        df['GENERAL VOTES'] = pd.to_numeric(df['GENERAL VOTES'],errors='coerce') # mysterious character
        df['GENERAL %'] = pd.to_numeric(df['GENERAL %'],errors='coerce')
    else:
        df['GENERAL VOTES'] = pd.to_numeric(df['GENERAL VOTES'],errors='raise')
        df['GENERAL %'] = pd.to_numeric(df['GENERAL %'],errors='raise')
    df['D'] = pd.to_numeric(df['D'],errors='coerce')
    if year=="2014": df.loc[df['CANDIDATE NAME (Last)']=='Assini','GENERAL %'] = 49.71
    df_winners = df.groupby(['STATE ABBREVIATION', 'D', 'PARTY']).sum().unstack().fillna(0)
    df_winners['winner'] = 'D'
    df_winners.loc[df_winners['GENERAL %']['R'] > df_winners['GENERAL %']['D'],'winner'] = "R"
    df_winners = df_winners.stack().reset_index()[['STATE ABBREVIATION','D','winner']].dropna()
    df = pd.merge(df,df_winners,how='left',on=['STATE ABBREVIATION', 'D'])
    df.loc[df['winner']==df['PARTY'],'GE WINNER INDICATOR'] = 'W'
    df_groups = df.groupby(['STATE ABBREVIATION','D','PARTY','CANDIDATE NAME (Last)']).sum()[['GENERAL VOTES']]
    df['VOTE_MAX'] = df.groupby(['STATE ABBREVIATION','D','PARTY'])['GENERAL VOTES'].transform(max)
    df = df.loc[df['GENERAL VOTES']==df['VOTE_MAX']]
    all_data[year] = df
    # What are the results?
    #print df_winners.groupby(['STATE ABBREVIATION','winner']).count().unstack()
    df_results = df_winners.groupby(['winner']).count()[['D']]
    total_representatives = df_results.iloc[0,0] + df_results.iloc[1,0]
    actual_d[year] = df_results.iloc[0,0]
    print "Election Results:\n",df_results, "\n"
    assert total_representatives==435

    # What are the total number of votes by party?
    df_byparty = df.groupby('PARTY',as_index=False).sum()[['PARTY','GENERAL VOTES']]
    df_byparty['total'] = df_byparty['GENERAL VOTES'].sum()
    df_byparty['share'] = df_byparty['GENERAL VOTES'] / df_byparty['total']
    df_byparty['seat_share'] = (df_byparty['share'] * total_representatives).round(0)
    nat_d[year] = df_byparty.iloc[0,4]
    print "Results Based on National Vote Share:\n",df_byparty, "\n"

    # What are the totals in each state? What would representation be if done on that level?
    df_bystate = df.groupby(['STATE ABBREVIATION', 'PARTY'],as_index=False).sum()
    df_statereps = df.groupby(['STATE ABBREVIATION', 'D'],as_index=False).count().groupby('STATE ABBREVIATION').count().rename(columns = {'D':'total_reps'})['total_reps']
    df_bystate = df_bystate.join(df_statereps,on='STATE ABBREVIATION').groupby(['STATE ABBREVIATION', 'PARTY','total_reps']).sum().unstack(1)['GENERAL VOTES'].fillna(0)
    df_bystate['total_votes'] = df_bystate['D'] + df_bystate['R']
    df_bystate = df_bystate.reset_index(level=1)
    df_bystate['reps_D'] = ((df_bystate['D']/df_bystate['total_votes']) * df_bystate['total_reps']).round(0)
    df_bystate['reps_R'] = ((df_bystate['R']/df_bystate['total_votes']) * df_bystate['total_reps']).round(0)
    print "Results Based on State Vote Share:\n",df_bystate[['reps_D','reps_R']].stack().reset_index().groupby('PARTY').sum(), "\n"

    # What are the margins in each election?
    df_byelection = df.groupby(['STATE ABBREVIATION','D', 'PARTY']).sum().unstack()
    df_byelection['margin'] = abs(df_byelection['GENERAL %']['D'] - df_byelection['GENERAL %']['R'])
    df_byelection['winner'] = "D"
    df_byelection.loc[df_byelection['GENERAL %']['R'] > df_byelection['GENERAL %']['D'],'winner'] = "R"
    df_margbyparty = df_byelection.groupby('winner').mean()
    print "Average Margin by Party:\n",df_margbyparty, "\n"
    df_byelection['count'] =  1
    df_byelection['margin'] =  df_byelection['margin'].round(0)
    df_byelection = df_byelection.reset_index()[['margin','winner','count']].dropna().groupby(['margin','winner']).count().unstack().fillna(0).reset_index()
    df_byelection['bucket'] = pd.cut(df_byelection['margin'],np.arange(0,100,5),include_lowest=True)
    df_byelection = df_byelection.groupby('bucket').sum()['count'].reindex(df_byelection['bucket'].drop_duplicates())
    df_byelection.to_csv('output/margin_buckets_'+year+'.csv')
    print "------------------------------------------------"

actual_d = dict()
nat_d = dict()
all_data = dict()

#analyze_election('results02.csv','2002') #Too many weird elections (see Louisiana)
analyze_election('results04.csv','2004')
analyze_election('results06.csv','2006')
analyze_election('results08.csv','2008')
analyze_election('results10.csv','2010')
analyze_election('results12.csv','2012')
analyze_election('results14.csv','2014')
seat_diff = pd.concat([pd.DataFrame.from_dict(actual_d, orient='index'),pd.DataFrame.from_dict(nat_d, orient='index')], axis=1).sort_index()
seat_diff.columns = ['actual','avg']
seat_diff['diff'] = seat_diff['actual'] - seat_diff['avg']
seat_diff.to_csv('output/seat differential.csv')
df_all = pd.concat(all_data)
df_votesbystate = df_all.groupby(['year','STATE ABBREVIATION','PARTY']).sum()[['GENERAL VOTES']].unstack()
df_votesbystate['Total'] = df_votesbystate['GENERAL VOTES']['D'] + df_votesbystate['GENERAL VOTES']['R']
df_votesbystate['Share_D'] = df_votesbystate['GENERAL VOTES']['D']/df_votesbystate['Total']
df_votesbystate['Share_R'] = df_votesbystate['GENERAL VOTES']['R']/df_votesbystate['Total']
df_seatsbystate = df_all.groupby(['year','STATE ABBREVIATION','D'],as_index=False).count().groupby(['year','STATE ABBREVIATION']).count().rename(columns = {'winner':'total_reps'})[['total_reps']]
df_votesbystate = df_votesbystate.join(df_seatsbystate)
df_votesbystate.columns = ['VOTES_D','VOTES_R','TOTAL','SHARE_D','SHARE_R','TOTAL_REPS']
df_votesbystate['REPS_STATE_D'] = (df_votesbystate['SHARE_D']*df_votesbystate['TOTAL_REPS']).round(0)
df_votesbystate['REPS_STATE_R'] = (df_votesbystate['SHARE_R']*df_votesbystate['TOTAL_REPS']).round(0)
df_actual = df_all.loc[df_all['GE WINNER INDICATOR']=='W'].groupby(['year','STATE ABBREVIATION','PARTY']).count().rename(columns = {'winner':'actual_reps'})[['actual_reps']].unstack().fillna(0)
df_actual.columns = ['REPS_ACT_D','REPS_ACT_R']
df_votesbystate = df_votesbystate.join(df_actual)
df_votesbystate['R_SURPLUS'] = (df_votesbystate['REPS_ACT_R'] - df_votesbystate['REPS_STATE_R'])/df_votesbystate['TOTAL_REPS']
df_rsurplus = df_votesbystate[['R_SURPLUS']].unstack(0).fillna(0)
df_rsurplus['AVG'] = df_rsurplus.mean(axis=1)
df_rsurplus.sort_values('AVG').to_csv('output/surplus_by_state.csv')
