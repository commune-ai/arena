

import commune as c
import datetime

class Account(c.Module):
   
    def __init__(self, password='12345',
                  user=None, 
                  metadata=None, 
                  signature_staleness=10, 
                  max_staleness=10000, 
                   **extra_metadata,
                  ):
        self.set_account(password=password, user=user, metadata=metadata)
        self.max_staleness = max_staleness
        self.signature_staleness = signature_staleness
        self.extra_metadata = extra_metadata
   
    def set_account(self, password, user=None, metadata=None):
        key = c.pwd2key(password)
        self.user = user
        self.metadata = metadata
        self.key = key
    
    def ticket(self, data=None, timestamp=None):
        data = data or {}
        timestamp = timestamp or c.timestamp()
        data = {
            'timestamp': timestamp,
            'data': data
        }
        data= self.key.sign(data, return_json=True)
        return data
    

    verified_data_path = 'verified_data'
    timestamp_seperator = '::'
    
    def get_file_timestamp(self, path):
        return int(path.split(self.timestamp_seperator)[-1].split('.')[0])
    
    def verify(self, data):  
        hash = c.hash(data)  
        address = data['address']
        timestamp = c.jload(data['data'])['timestamp']
        staleness = c.timestamp() - timestamp
        if staleness > self.signature_staleness:
            return False
        path = self.resolve_path(self.verified_data_path + '/' + address +'/'  + hash + self.timestamp_seperator + str(timestamp) + '.json')
        if c.exists(path):
            return False
        verified =  c.verify(data)
        self.put(path, data)
        return verified
    

    def ticket2data(self, ticket):
        return c.jload(ticket['data'])
    
    def files(self):
        return self.glob(self.verified_data_path)
    
    def stale_files(self, max_staleness=None):
        if max_staleness == None:
            max_staleness = self.max_staleness
        files = self.files()
        current_timestamp = c.timestamp()
        stale_files = []
        for file in files:
            file_timestamp = self.get_file_timestamp(file)
            staleness = current_timestamp - file_timestamp
            if staleness > max_staleness:
                stale_files.append(file)
        
        return stale_files
    

    def rm_stale_files(self, max_staleness=None):
        stale_files = self.stale_files(max_staleness)
        num_files_removed = 0
        print('Removing stale files: {}'.format(stale_files))

        for file in stale_files:
            c.print(self.rm(file))
            num_files_removed += 1
        return {'success': 'Stale files removed successfully',
                'num_files_removed': len(stale_files), 
                'num_files': self.num_files() }
    

    def num_files(self):
        return len(self.files())
                
                
    
    def timestamp2file(self):
        files = self.files()
        timestamp2file = {}
        for file in files:
            timestamp = self.get_file_timestamp(file)
            timestamp2file[timestamp] = file
        return timestamp2file

    def test_account(self):
        ticket = self.ticket()
        assert self.verify(ticket), 'Verification failed'
        return {'success': 'Account tested successfully'}
    

    def test_replay_attack(self, password='12345', data='1'):
        ticket = self.ticket(data)
        assert self.verify(ticket) == True, 'Verification failed'
        assert self.verify(ticket) == False, 'Replay attack failed'
        return {'success': 'Replay attack tested successfully'}


    def state_dict(self):
        return {
            'user': self.user,
            'metadata': self.metadata,
            'key': self.key.ss58_address,
            **self.extra_metadata
        }
    
    def public_key(self):
        return self.key.ss58_address
    
    def address(self):
        return self.key.ss58_address



    def my_history(self, 
                   columns=['time', 'model', 'prompt', 'response', 'score', 'temperature', 'model2score'], 
                   sort_by='time',
                     ascending=False,
                       model=None):
        df = c.df(self.get_history(model=model))
        if len(df) == 0:
            st.error('No history found, enter the arena')
            return df
        # convert timestmap to human readable
        df['score'] = df['mean']
        df['time'] = df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime('%m-%d %H:%M'))
        df = df[columns].sort_values(sort_by, ascending=ascending)
        df = df.set_index('time')
        df.sort_index(inplace=True)
        return df
    
    @classmethod
    def create(cls, password='12345', **kwargs):
        return cls(password=password, **kwargs).state_dict()
    

    def add_metadata(self, **metadata):
        self.metadata = metadata
        return self.state_dict()


    
    def signin(self):
        import streamlit as st
        pwd = st.text_input('pwd', 'fam', type='password')
        key = c.pwd2key(pwd)
        self.key = key
        st.write('Public Address')
        st.code(key.ss58_address)
        
        return self.key