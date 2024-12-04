from django.shortcuts import * # type: ignore
from django.http import HttpResponse # type: ignore
from django.contrib.auth import *
from  .models import *
from .forms import *
import hashlib
from web3 import Web3
 
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

#-------------------HERE IS THE BLOCKCHAIN CODE-------------------
def DocMap_init():        
    DocMap_contract_abi = [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"name": "documentHashes",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "docName",
				"type": "string"
			}
		],
		"name": "getDocumentHash",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "docName",
				"type": "string"
			}
		],
		"name": "removeDocument",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "docName",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "hash",
				"type": "string"
			}
		],
		"name": "setDocumentHash",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]
    DocMap_contract_address = "0x9Ad3CE8Af4D7eedDC4D1fAEbDF91003fe514B848"
    DocMap_contract = w3.eth.contract(address=DocMap_contract_address, abi=DocMap_contract_abi)
    w3.eth.default_account = w3.eth.accounts[0]
    return DocMap_contract
def getDocumentHash(DocMap_contract, documentName):
    document_hash = DocMap_contract.functions.getDocumentHash(documentName).call()
    return document_hash
def setDocumentHash(DocMap_contract, documentName, documentHash):
    transcaction_hash = DocMap_contract.functions.setDocumentHash(documentName,documentHash).transact()
    reciept = w3.eth.wait_for_transaction_receipt(transcaction_hash)
    return reciept
def removeDocument(DocMap_contract, documentName):
    reciept = DocMap_contract.functions.removeDocument(documentName).transact()
    return reciept
#-----------------------------------------------------------------

def RegisterView(request):
    message = None
    if request.method == 'POST':
        formSignIn = SignInForm(request.POST)
        username = request.POST.get('username')
        ##Checks if the user exists
        if User.objects.filter(username=username).exists():
            message = "User Already Exists"
        #If the user does not check validity and save the form
        elif formSignIn.is_valid():
            #If the form is valid then safe to the database and redirect
            #formSignIn.save()
            userInstace = User(username=username)
            userInstace.set_password(request.POST.get('password'))
            userInstace.save()
            return redirect('signInPage')
    else:
        formSignIn = SignInForm()
    
    
    return render(request,'register.html',{'form':formSignIn, 'message':message})



def success(request):
    return HttpResponse("Logged In")
# Create your views here.

def WelcomePageView(request):
    test_contract = DocMap_init()
    setDocumentHash(test_contract,"Doc11","123")
    getDocumentHash(test_contract,"Doc1111")
    removeDocument(test_contract,"Doc11")
    return render(request, 'welcome.html')

def UploadPortalView(request):
    # This statement below is used to redirect the user if they have not signed in
    doc_contract = DocMap_init()    
    if not request.user.is_authenticated:
        return redirect("signInPage")
    associatedDocs = None
    title = None
    transaction_hash = ""
    doc_Titles =[""]
    receipt_message = ""
    if request.method == 'POST':
        form = DocumentsForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            title = uploaded_file.name
            fileContent = uploaded_file.read()
            fileHash = hashlib.sha256(fileContent).hexdigest()

            docuInstace = Document(docname=title)
            author = User.objects.get(username=str(request.user))
                        
            ##Check if the document exists
            existing_doc = Document.objects.filter(docname=str(title))
            if existing_doc:
                for doc in existing_doc:
                    existing_doc_author = doc.authors.all()
                    for authorofDoc in existing_doc:
                        ##If the user is the author of the document then you can upated the existing doc, otherwise you will not overwrite
                        if author.username == str(request.user):
                            #transaction_receipt = setDocumentHash(doc_contract,str(title),fileHash)
                            #transaction_hash = str(w3.to_hex(transaction_receipt['transactionHash']))
                            #transaction_to = str(transaction_receipt['to'])
                            #transaction_from = str(transaction_receipt['from'])
                            #transaction_cost =  str(transaction_receipt['gasUsed'])
                            #transaction_receipt_dict = dict(hashID = transaction_hash, toAccount = transaction_to, fromAccount=transaction_from, cost=transaction_cost)
                            print("temp print out")
                            #request.session['receipt_dict'] = transaction_receipt_dict
            ##Otherwise Save
            else:
                docuInstace.save()
                transaction_receipt = setDocumentHash(doc_contract,str(title),fileHash)
                transaction_hash = str(w3.to_hex(transaction_receipt['transactionHash']))
                transaction_to = str(transaction_receipt['to'])
                transaction_from = str(transaction_receipt['from'])
                transaction_cost =  str(transaction_receipt['gasUsed'])
                transaction_receipt_dict = dict(hashID = transaction_hash, toAccount = transaction_to, fromAccount=transaction_from, cost=transaction_cost)
                request.session['receipt_dict'] = transaction_receipt_dict
                ##This line below sets the author of the document
                docuInstace.authors.set([request.user])
                receipt_message = "View Your Receipt"
                ##
                
            associatedDocs = author.documents.all()
            for doc in associatedDocs:
                doc_Titles.append(doc.docname)
    else:
        form = DocumentsForm()
    return render(request, 'UploadPortal.html', {'form':DocumentsForm,'AuthorDocs':doc_Titles, 'receipt_message': receipt_message})

def ReceiptView(request):
    receiptDict = request.session.get('receipt_dict', {})
    transaction_id = receiptDict.get("hashID")
    transaction_to = receiptDict.get("toAccount")
    transaction_from = receiptDict.get("fromAccount")
    transaction_cost = receiptDict.get("cost")
    return render(request, 'receipt.html',{'id': transaction_id, 'to': transaction_to, 'from':transaction_from, 'cost':transaction_cost})    

def VerifyPortalView(request):
    doc_contract = DocMap_init()  
    authentic_message = ""
    if request.method == 'POST':
        form = DocumentsForm(request.POST, request.FILES) 
        if form.is_valid():
            upload_file = request.FILES['file']
            title = upload_file.name
            fileContent = upload_file.read()
            fileHash = hashlib.sha256(fileContent).hexdigest()
            stored_file_hash = getDocumentHash(doc_contract,str(title))
            if stored_file_hash == fileHash :
                authentic_message = "The document you have uploaded is authentic"
            else:
                authentic_message = "The document you have uploaded is inauthentic"
            
            #
            #try:
                
            #    doc = Document.objects.get(docname=str(title))
            #    document_title = "The document that you have uploaded originally called '"+ doc.docname + "' is authentic"
            #except Document.DoesNotExist:
            #    document_title = "This document is not authentic"
    else:
        form = DocumentsForm()
    return render(request, 'VerifyPortal.html', {'form':DocumentsForm , 'auth_message':authentic_message} )


def SignInView(request):
    #**LOGS OUT USER** 
    logout(request) 
    #*****************
    if request.method == 'POST':
        formSignIn = LogInForm(request.POST)
        
        if formSignIn.is_valid():
            usernameInput = request.POST.get('username')
            passwordInput = request.POST.get('password')
            
            userInstance = authenticate(request,username=usernameInput, password=passwordInput)
                
            if userInstance is not None: 
                login(request, userInstance)
                return redirect('UploadPage')
    else:
        formSignIn = LogInForm()
    return render(request,'login.html',{'form':formSignIn}) ##The {form : formSignIn} passes the form to the html
    