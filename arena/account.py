

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
        data = ticket.copy()
        tickets = data.pop('tickets')
        results = []
        timestamp = ticket['timestamp']
        staleness = c.timestamp() - timestamp
        assert staleness < max_staleness, f'Staleness {staleness} > {max_staleness}'
        for user, ticket in tickets.items():
            print(data, 'data')
            result = c.verify(data, signature=ticket['signature'], address=ticket['address'])
            results += [result]
        print(results)
        return all(results)
    

    def test_account(self, n=10, data={'None': 'None'}):
        results = []
        for i in range(n):
            ticket = self.ticket(data)
            assert self.verify_ticket(ticket), 'Ticket verification failed'
            results += [{'success': 'Account tested successfully', 'address': ticket['tickets']['billy']['address']}]
        return results
    


    def state_dict(self):
        return {
            'user': self.user,
            'data': self.data,
            'key': self.key.ss58_address,
        }
    
    def public_key(self):
        return self.key.ss58_address
    
    def ticket(self, data = None ):
        data = c.copy(data)
        if data is None:
            data = {'timestamp': c.time()}
        if 'timestamp' not in data:
            data['timestamp'] = c.time()
        signature = self.key.sign(data).hex()
        ticket = {
                'address': self.key.ss58_address, 
                'signature': signature,
                }
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
