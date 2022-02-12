import keyring

print('you may need to do ctrl+shift+v if you cant paste')
cid = input('please paste your client id and press enter: ')
csc = input('please paste your client secret and press enter: ')

keyring.set_password('spotify', 'cid', cid.strip())
keyring.set_password('spotify', 'csc', csc.strip())

print('all done')
print('you can run this as many time as you want but i only need it once')