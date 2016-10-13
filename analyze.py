import pandas as pd
import numpy as np
import re
import csv
import json

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
    df_quantile = df_byelection.dropna().set_index('winner',append=True)[['margin']].unstack().quantile([.25,.75])
    df_quantile.columns = ['D','R']
    quantiles[year] = df_quantile.to_dict()
    df_byelection = df_byelection.reset_index()[['margin','winner','count']].dropna().groupby(['margin','winner']).count().unstack().fillna(0).reset_index()
    df_byelection['bucket'] = pd.cut(df_byelection['margin'],np.arange(0,100,5),include_lowest=True)
    bucket_range = pd.DataFrame()
    bucket_range['buckets'] =  pd.cut(range(0,99),np.arange(0,100,5),include_lowest=True).dropna()
    df_byelection = df_byelection.groupby('bucket').sum()['count'].reindex(bucket_range['buckets'].drop_duplicates())
    df_byelection = df_byelection.reset_index()
    df_byelection.columns = ['bucket','D','R']
    df_byelection['bucket'] = df_byelection['bucket'].str.replace(', ',' - ').str.replace('[','').str.replace(']','').str.replace('(','')
    df_byelection = df_byelection.fillna(value=0, axis=1)
    df_byelection.to_csv('output/margin_buckets_'+year+'.csv',index=False)
    print "------------------------------------------------"

actual_d = dict()
nat_d = dict()
all_data = dict()
quantiles = dict()

#analyze_election('results02.csv','2002') #Too many weird elections (see Louisiana)
analyze_election('results04.csv','2004')
analyze_election('results06.csv','2006')
analyze_election('results08.csv','2008')
analyze_election('results10.csv','2010')
analyze_election('results12.csv','2012')
analyze_election('results14.csv','2014')

# print quantiles

# Natl vs Elected share of seats (Dem)
seat_diff = pd.concat([pd.DataFrame.from_dict(actual_d, orient='index'),pd.DataFrame.from_dict(nat_d, orient='index')], axis=1).sort_index()
seat_diff.columns = ['actual','avg']
seat_diff['diff'] = seat_diff['actual'] - seat_diff['avg']
seat_diff.reset_index().to_csv('temp/seat_differential.csv',index=False)
df_all = pd.concat(all_data)

# Run by state analysis
df_votesbystate = df_all.groupby(['year','STATE ABBREVIATION','PARTY']).sum()[['GENERAL VOTES']].unstack()
df_votesbystate['Total'] = df_votesbystate['GENERAL VOTES']['D'] + df_votesbystate['GENERAL VOTES']['R']
df_votesbystate['Share_D'] = df_votesbystate['GENERAL VOTES']['D']/df_votesbystate['Total']
df_votesbystate['Share_R'] = df_votesbystate['GENERAL VOTES']['R']/df_votesbystate['Total']
df_seatsbystate = df_all.groupby(['year','STATE ABBREVIATION','D'],as_index=False).count().groupby(['year','STATE ABBREVIATION']).count().rename(columns = {'winner':'total_reps'})[['total_reps']]
df_votesbystate = df_votesbystate.join(df_seatsbystate)
df_votesbystate.columns = ['VOTES_D','VOTES_R','TOTAL','SHARE_D','SHARE_R','TOTAL_REPS']
df_votesbystate['REPS_STATE_D'] = (df_votesbystate['SHARE_D']*df_votesbystate['TOTAL_REPS'])#.round(0)
df_votesbystate['REPS_STATE_R'] = (df_votesbystate['SHARE_R']*df_votesbystate['TOTAL_REPS'])#.round(0)
df_actual = df_all.loc[df_all['GE WINNER INDICATOR']=='W'].groupby(['year','STATE ABBREVIATION','PARTY']).count().rename(columns = {'winner':'actual_reps'})[['actual_reps']].unstack().fillna(0)
df_actual.columns = ['REPS_ACT_D','REPS_ACT_R']
df_votesbystate = df_votesbystate.join(df_actual)
df_votesbystate['R_SURPLUS'] = (df_votesbystate['REPS_ACT_R'] - df_votesbystate['REPS_STATE_R'])/df_votesbystate['TOTAL_REPS']
# print df_votesbystate
df_rsurplus = df_votesbystate[['R_SURPLUS']].unstack(0).fillna(0)
df_rsurplus['AVG'] = df_rsurplus.mean(axis=1)
df_rsurplus['Total Reps'] = df_votesbystate['TOTAL_REPS'].unstack(0)[['2004']]
df_rsurplus = df_rsurplus.reset_index()
df_states_full = df_all.groupby(['STATE','STATE ABBREVIATION'],as_index=False).sum()[['STATE','STATE ABBREVIATION']].rename(columns = {'STATE ABBREVIATION':'State','STATE':'State_Full'})
df_rsurplus.columns = ['State','y2004','y2006','y2008','y2010','y2012','y2014','Average','Total_Reps']
df_rsurplus = pd.merge(df_rsurplus,df_states_full,how='left',on='State')
df_rsurplus['Mis_Reps'] = df_rsurplus['Total_Reps'] * abs(df_rsurplus['Average'])
df_rsurplus = df_rsurplus.drop_duplicates('State')
df_rsurplus.sort_values('Average').to_csv('temp/surplus_by_state.csv',index=False)

# Vote vs Seat share by year
df_votesbyyear = df_all.groupby(['year','PARTY']).sum()[['GENERAL VOTES']].unstack()
df_votesbyyear['Total'] = df_votesbyyear['GENERAL VOTES']['D'] + df_votesbyyear['GENERAL VOTES']['R']
df_votesbyyear['share_D'] = df_votesbyyear['GENERAL VOTES']['D'] / df_votesbyyear['Total']
df_votesbyyear['share_R'] = df_votesbyyear['GENERAL VOTES']['R'] / df_votesbyyear['Total']
df_votesbyyear = df_votesbyyear[['share_D','share_R']].reset_index()
df_votesbyyear.to_csv('temp/vote_share_by_year.csv',index=False)
df_seatsbyyear = df_all.loc[df_all['GE WINNER INDICATOR']=='W'].groupby(['year','winner']).count()[['GENERAL VOTES']].rename(columns = {'GENERAL VOTES':'seats'}).unstack()
df_seatsbyyear['Total'] = df_seatsbyyear['seats']['D'] + df_seatsbyyear['seats']['R']
df_seatsbyyear['share_D'] = df_seatsbyyear['seats']['D'] / df_seatsbyyear['Total']
df_seatsbyyear['share_R'] = df_seatsbyyear['seats']['R'] / df_seatsbyyear['Total']
df_seatsbyyear = df_seatsbyyear[['share_D','share_R']].reset_index()
df_seatsbyyear['diff'] = df_seatsbyyear['share_D'] - df_votesbyyear['share_D']
#print df_seatsbyyear
df_seatsbyyear.to_csv('temp/seat_shares_by_year.csv',index=False)

#All years vote margins
df_margins = df_all.groupby(['STATE ABBREVIATION','year','D','winner', 'PARTY']).sum().unstack().dropna() #Should the uncontesteds be dropped?
df_margins = df_margins['GENERAL %']
df_margins.columns = ['D_pct','R_pct']
df_margins['margin'] = abs(df_margins['D_pct'] - df_margins['R_pct'])
quantiles['all'] = df_margins['margin'].unstack().quantile([.25,.75]).to_dict()
df_margins['bucket'] = pd.cut(df_margins['margin'],np.arange(0,100,5),include_lowest=True)
df_margins['count'] =  1
print df_margins.loc[df_margins['margin'] > 80]
df_margins = df_margins.reset_index()
df_margins = df_margins.groupby(['bucket','winner']).sum()['count'].unstack().fillna(0).reset_index()
df_margins['bucket'] = df_margins['bucket'].str.replace(', ',' - ').str.replace('[','').str.replace(']','').str.replace('(','')
df_margins.to_csv('temp/margins_aggregated.csv',index=False)

with open('output/iqr.json', 'w') as fp:
    json.dump(quantiles, fp)

# Eliminate blank rows
for f in ['seat_differential.csv','surplus_by_state.csv','vote_share_by_year.csv','seat_shares_by_year.csv','margins_aggregated.csv']:
    in_file = open('temp/'+f, 'rb')
    output = open('output/'+f, 'wb')
    writer = csv.writer(output)
    for row in csv.reader(in_file):
        if any(row):
            writer.writerow(row)
    in_file.close()
    output.close()
