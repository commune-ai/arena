

import commune as c
import datetime

class Account(c.Module):
   
    def __init__(self, password='12345',
                  user=None, 
                  metadata=None, 
                  signature_staleness=10, 
                  max_file_staleness=10000, 
                   **extra_metadata,
                  ):
        self.set_account(password=c.hash(password), user=user, metadata=metadata)
        self.max_file_staleness = max_file_staleness
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

    def sign(self, data, **kwargs):
        return self.key.sign( data, **kwargs)
    
    def verify(self, data,  **kwargs):
        return self.key.verify( data, **kwargs)
    
    def encyrpt(self, data,  **kwargs):
        return self.key.encrypt(data , **kwargs)
        
    def decrypt(self, data, **kwargs):
        return self.key.decrypt( data, **kwargs)


    verified_data_path = 'verified_data'
    timestamp_seperator = '::'

    def ticket2address(self, ticket):
        return ticket['address']
    
    def get_file_timestamp(self, path):
        return int(path.split(self.timestamp_seperator)[-1].split('.')[0])
    
    def verify_ticket(self, data, max_staleness=None):

        hash = c.hash(data)  
        address = data['address']
        timestamp = c.jload(data['data'])['timestamp']
        staleness = c.timestamp() - timestamp
        max_staleness = max_staleness or self.signature_staleness
        assert staleness < max_staleness, f'Staleness {staleness} > {max_staleness}'
        path = self.resolve_path(self.verified_data_path + '/' + address +'/'  + hash + self.timestamp_seperator + str(timestamp) + '.json')
        assert not c.exists(path), f'Verified data already exists {path}'
        self.key.verify(data)
        if 'data' in data:
            data = c.jload(data['data'])
        return data
    

    def ticket2data(self, ticket):
        return c.jload(ticket['data'])
    
    def files(self):
        return self.glob(self.verified_data_path)
    
    def stale_files(self, max_staleness=None):
        if max_staleness == None:
            max_staleness = self.max_file_staleness
        files = self.files()
        current_timestamp = c.timestamp()
        stale_files = []
        for file in files:
            file_timestamp = self.get_file_timestamp(file)
            staleness = current_timestamp - file_timestamp
            if staleness > max_staleness:
                stale_files.append(file)
        
        return stale_files
    

    def rm_stale_files(self, max_file_staleness=None):
        stale_files = self.stale_files(max_file_staleness)
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
        assert self.verify_ticket(ticket), 'Verification failed'
        return {'success': 'Account tested successfully'}
    

    def test_replay_attack(self, password='12345', data='1'):
        ticket = self.ticket(data)
        assert self.verify_ticket(ticket) == True, 'Verification failed'
        assert self.verify_ticket(ticket) == False, 'Replay attack failed'
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


    def create_ticket(self, data = None, password=None, account=None):
        if not data:
            data = c.time()
        if account == None:
            account = Account(password=password) if password else self
        return {
                'address': account.key.ss58_address, 
                'signature': account.sign(data).hex()
                }

    def add_metadata(self, **metadata):
        self.metadata = metadata
        return self.state_dict()