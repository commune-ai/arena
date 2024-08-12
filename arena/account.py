

import commune as c

class Account(c.Module):
   
    def __init__(self, 
                 user='billy', 
                  password='12345',
                  salt=None,
                  data=None, 
                  ):
        self.set_account(password=password, user=user, data=data, salt=salt)

    def set_account(self, user=None , password=None, data=None, salt=None):
        user_seed = c.hash(str(user)+str(password) + str(salt))
        self.user = user
        self.data = data
        self.key = c.pwd2key(user_seed)
        return self.key

    def sign(self, data, **kwargs):
        return self.key.sign( data, **kwargs)
    
    def verify(self, data,  **kwargs):
        return self.key.verify( data, **kwargs)
    
    def encyrpt(self, data,  **kwargs):
        return self.key.encrypt(data , **kwargs)
        
    def decrypt(self, data, **kwargs):
        return self.key.decrypt( data, **kwargs)
    
    
    def verify_ticket(self, ticket, max_staleness=10):
        tickets = ticket.pop('tickets')
        results = []
        timestamp = c.jload(ticket)['timestamp']
        staleness = c.timestamp() - timestamp
        assert staleness < max_staleness, f'Staleness {staleness} > {max_staleness}'
        for user, ticket in tickets.items():
            result = c.verify(ticket['data'], signature=ticket['signature'], address=ticket['address'])
            results += [result]
        return all(results)
    

    def test_account(self, n=10):
        results = []
        for i in range(n):
            ticket = self.ticket()
            print(ticket)
            assert self.verify_ticket(ticket), 'Verification failed'
            results += [{'success': 'Account tested successfully'}]
        return results
    


    def state_dict(self):
        return {
            'user': self.user,
            'data': self.data,
            'key': self.key.ss58_address,
        }
    
    def public_key(self):
        return self.key.ss58_address
    
    def ticket(self, data = {'a': 1}, password=None ):

        ticket = {
                'address': self.key.ss58_address, 
                'signature': self.sign(data).hex(),
                'timestamp': c.timestamp(),
                }
        if isinstance(data, dict):
            ticket['keys'] = list(data.keys())
        if not 'tickets' in data:
            data['tickets'] = {}
        data['tickets'][self.user] = ticket
        return data

    def __repr__(self):
        return f'Account(user={self.user} key={self.key.ss58_address} data={self.data})'
    def __str__(self):
        return self.__repr__()
    
    @classmethod
    def new_account(cls, user='alice', password='bob', salt=None):
        return cls(user=user, password=password, salt=salt)
