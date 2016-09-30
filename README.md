# iCloudContacts
Pulls iCloud Contacts for an account. No dependencies. No user notification. Very quick. Tokens / normal credentials supported.

**iCloudContacts** will pull all contacts from the iCloud CardDav server (all iCloud Contacts for any iCloud user) and print them to stdout as well as save them to a text file. It works by taking an apple ID and corresponding password (or an MMeAuthToken if you have one), grabbing a MMeAuthToken, which is then supplied to the CardDav server to pull all the HREFS for the VCF cards on an iCloud account, and then uses those HREFS to pull the actual VCF data. It then goes through this VCF data and outputs the Contact Name and Telephone Number.

***Example Usage***: python iCloudContacts.py

```
Input: AppleID or DSID

Input: Password or MMeAuthToken

Output: John Doe (914) 879-8824

Output: Found 1 contacts for user bobloblaw@icloud.com! Wrote contacts to bobloblaw@icloud.com.txt
```



**To be implemented features**

- [ ] Add feature to combine all contacts into one VCF card

- [ ] Make output contain more VCF information, IE social media, nicknames, etc.
