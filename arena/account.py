

import commune as c

class Account(c.Module):
   
    def __init__(self, 
                 user='billy', 
                  password='12345',
                  salt=None,
                  data=None, 
                  role = 'user', 
                  ):
        self.set_account(password=password, user=user, data=data, salt=salt, role=role)

    def set_account(self, user=None , password=None, data=None, salt=None, role='user'):
        user_seed = c.hash(str(user)+str(password) + str(salt))
        self.role = role
        self.user = user
        self.data = data
        self.key = c.pwd2key(user_seed)
        return self.key
    
    def verify(self, ticket, max_staleness=10):
        data = c.copy(ticket)
        signatures = data.pop('signatures')
        results = []
        timestamp = ticket['timestamp']
        staleness = c.timestamp() - timestamp
        assert staleness < max_staleness, f'Staleness {staleness} > {max_staleness}'
        for role, ticket in signatures.items():
            ticket = c.copy(ticket)
            ticket_data = {key: data[key] for key in ticket['data_keys']}
            result = c.verify(ticket_data, signature=ticket['signature'], address=ticket['address'])
            results += [result]
        return all(results)
    

    @classmethod
    def test(cls, n=10, ticket={'a': 1}):
        results = []
        for i in range(n):
            self = cls(user=str(i), role=f'user{i}')
            ticket = self.sign(ticket)
            assert self.verify(ticket), 'Ticket verification failed'
        result = self.verify(ticket)
        assert result, 'Ticket verification failed'
        return {'result': result, 'ticket': ticket}
    


    def state_dict(self):
        return {
            'user': self.user,
            'data': self.data,
            'key': self.key.ss58_address,
        }
    
    def public_key(self):
        return self.key.ss58_address
    
    def sign(self, data = None , role=None):
        role = role or self.role
        data = c.copy(data or {})
        if 'timestamp' not in data:
            data['timestamp'] = c.time()
        signatures = data.pop('signatures', {})
        signature = self.key.sign(data).hex()

        ticket = {
                'signature': signature,
                'crypto_type': self.key.crypto_type,
                'data_keys' : list(data.keys())
                }
        if role:
            ticket['address'] = self.key.ss58_address
            signatures[role] = ticket
        else:
            signatures[self.key.ss58_address] = ticket
        data['signatures'] = signatures
        return data

    def __repr__(self):
        return f'Account(user={self.role} key={self.key.ss58_address} data={self.data})'
    def __str__(self):
        return self.__repr__()
    
    @classmethod
    def new_account(cls, user='alice', password='bob', salt=None):
        return cls(user=user, password=password, salt=salt)
