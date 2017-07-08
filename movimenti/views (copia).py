# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse    
from movimenti.models import investimento, transazione, titolo, tipo_transazione, tipo, posizione
from django.db.models import Sum, Count


# Create your views here.



def index(request):
	#tipo_transazione_id
	# 1: acquisto
	# 2: vendita
	# 3: dividendo
	# 4: imposta statale 12.5% o 26%
	# 5: imposta di altro tipo
	# 6: carico del portafoglio in seguito ad operazione societaria
	# 7: scarico
	# 8: rimborso

	elenco = posizione.objects.filter(opened=True).values('id').distinct()
	
	data = []
	altri_dati = {}
	
	totale_gain_aperti = 0
	totale_imposte_aperti = 0
	totale_commissione_aperti = 0
   		
	for year in elenco:
    		single_data={}
    		single_data['label'] = year['id']
    		single_data['titolo'] = transazione.objects.filter(posizione=year['id'])[0].titolo
    		
    		q = transazione.calcoli.totale(year['id'])
		tot = 0
		for i in q:
			if i.tipo_id ==1 or  i.tipo_id == 6:
				tot=tot+i.quantity
			elif  i.tipo_id ==2  or i.tipo_id ==7  or i.tipo_id ==8:
				tot=tot-i.quantity
			
    		single_data['quantity'] = tot
    		
		tot = 0
		for i in q:
			if i.tipo_id ==1 or  i.tipo_id == 6 or  i.tipo_id == 4 or  i.tipo_id == 5:
				tot=tot - (i.importo or 0) - (i.costo or 0) - (i.imposta or 0) - (i.rateo or 0) + (i.imposta_dietimi or 0)
			elif  i.tipo_id ==2  or i.tipo_id ==7  or i.tipo_id ==8 or i.tipo_id ==3:
				tot=tot + (i.importo or 0) - (i.costo or 0) - (i.imposta or 0) + (i.rateo or 0) - (i.imposta_dietimi or 0) 
    		
    		if int(single_data['quantity']):
    			single_data['cu'] =  float(tot) / float(single_data['quantity'])
    		single_data['gain'] = "%.2f" % tot
    		totale_gain_aperti = totale_gain_aperti + tot
    		
		tot = 0
		for i in q:
			if i.tipo_id ==1 or  i.tipo_id == 6 or  i.tipo_id == 4 or  i.tipo_id == 5:
				tot=tot + (i.imposta or 0) - (i.imposta_dietimi or 0)
			elif  i.tipo_id ==2  or i.tipo_id ==7  or i.tipo_id ==8 or i.tipo_id ==3:
				tot=tot + (i.imposta or 0) + (i.imposta_dietimi or 0)
    		
    		
    		single_data['imposte'] = tot
    		totale_imposte_aperti = totale_imposte_aperti + tot
    		
    		single_data['commissioni']=(transazione.objects.filter(posizione_id=year['id']).aggregate(Sum('costo'))['costo__sum'] or 0)
    		totale_commissione_aperti = totale_commissione_aperti + single_data['commissioni']
    		
    		qq = transazione.calcoli.durata(year['id'])
    		single_data['inizio'] = qq[0]
    		
    		data = data + [single_data]
	
	altri_dati['totale_imposte_aperti'] = totale_imposte_aperti
	altri_dati['totale_gain_aperti'] = totale_gain_aperti
	altri_dati['totale_commissione_aperti'] = totale_commissione_aperti
	
	#seconda parte - investimenti chiusi
		
	elenco = posizione.objects.filter(opened=False).values('id').distinct().order_by('-id')
	#tipo_transazione_id
	# 1: acquisto
	# 2: vendita
	# 3: dividendo
	# 4: imposta statale 12.5% o 26%
	# 5: imposta di altro tipo
	# 6: carico del portafoglio in seguito ad operazione societaria
	# 7: scarico
	# 8: rimborso
	
	dat = []
	totale_gain_chiusi = 0
	totale_imposte_chiusi = 0
	totale_commissione_chiusi = 0
   		
	for year in elenco:
    		single_data={}
    		single_data['label'] = year['id']
    		single_data['titolo'] = transazione.objects.filter(posizione=year['id'])[0].titolo
    		
    		q = transazione.calcoli.totale(year['id'])

		tot = 0
		for i in q:
			if i.tipo_id ==1 or  i.tipo_id == 6 or  i.tipo_id == 4 or  i.tipo_id == 5:
				tot=tot - (i.importo or 0) - (i.costo or 0) - (i.imposta or 0) - (i.rateo or 0) + (i.imposta_dietimi or 0)
			elif  i.tipo_id ==2  or i.tipo_id ==7  or i.tipo_id ==8 or i.tipo_id ==3:
				tot=tot + (i.importo or 0) - (i.costo or 0) - (i.imposta or 0) + (i.rateo or 0) - (i.imposta_dietimi or 0) 
    		
    		
    		single_data['gain'] = "%.2f" % tot
    		totale_gain_chiusi = totale_gain_chiusi + tot
    		
		tot = 0
		for i in q:
			if i.tipo_id ==1 or  i.tipo_id == 6 or  i.tipo_id == 4 or  i.tipo_id == 5:
				tot=tot + (i.imposta or 0) - (i.imposta_dietimi or 0)
			elif  i.tipo_id ==2  or i.tipo_id ==7  or i.tipo_id ==8 or i.tipo_id ==3:
				tot=tot + (i.imposta or 0) + (i.imposta_dietimi or 0)
    		
    		totale_imposte_chiusi = totale_imposte_chiusi + tot
    		single_data['imposte'] = tot
    		single_data['commissioni']=(transazione.objects.filter(posizione_id=year['id']).aggregate(Sum('costo'))['costo__sum'] or 0)
    		totale_commissione_chiusi = totale_commissione_chiusi + single_data['commissioni']
    		
    		#ricavo per posizione
    		tot = 0
		for i in q:
			if i.tipo_id ==1 or  i.tipo_id == 6:
				tot=tot - (i.importo or 0) - (i.costo or 0) 
			elif  i.tipo_id ==2  or i.tipo_id ==7  or i.tipo_id ==8:
				tot=tot + (i.importo or 0) - (i.costo or 0) 
    	
    		single_data['ricavo'] = tot
    		
    		
    		#altri utili: rateo, dividendi,...
    		tot = 0
		for i in q:
			if i.tipo_id ==1 or  i.tipo_id == 6:
				tot=tot  - (i.rateo or 0) + (i.imposta_dietimi or 0)
			elif  i.tipo_id ==2  or i.tipo_id ==7  or i.tipo_id ==8:
				tot=tot + (i.rateo or 0) - (i.imposta_dietimi or 0)
			elif  i.tipo_id ==3:
				tot=tot + (i.importo or 0) - (i.imposta or 0)
    	
    		single_data['altriutili'] = tot
    		
    		
    		qq = transazione.calcoli.durata(year['id'])
    		single_data['inizio'] = qq[0]
    		single_data['fine'] = qq[1]
    		single_data['delta'] = qq[2]
    			
    		dat = dat + [single_data]
	
	altri_dati['totale_imposte_chiusi'] = totale_imposte_chiusi
	altri_dati['totale_gain_chiusi'] = totale_gain_chiusi
	altri_dati['totale_commissione_chiusi'] = totale_commissione_chiusi
	
	

	return render(request, 'detail.html', {'data' : data, 'dat' : dat, 'altri_dati' : altri_dati},)
	
def popup(request):	
	worker = transazione.objects.get(id=request.GET.get('id'))
	elenco = posizione.objects.filter(titolo=worker.titolo).values('id','opened').distinct()
	attuale = request.GET.get('attuale')
	
	dat = []
   		
	for year in elenco:
    		single_data={}
    		single_data['label'] = year['id']
    		
    		qq = transazione.calcoli.durata(year['id'])
    		single_data['inizio'] = qq[0]
    		single_data['fine'] = qq[1]
    		single_data['aperta'] = year['opened']
    			
    		dat = dat + [single_data]
     
	return render(request, 'popupadvance.html', {'worker': worker, 'dat': dat, 'attuale': attuale})
	
def return_popup(request):
	#import wdb; wdb.set_trace()
	
	p = get_object_or_404(transazione, pk=request.GET['id'])
	p.posizione_id = request.POST['choice']
	p.save()

	return HttpResponseRedirect('/admin/movimenti/transazione/'+str(p.id))
	
	
def popup_importa(request):	
	worker = request.GET.get('id')
	dat = []
	if worker != 'new':
		nuova=0
		elenco = transazione.objects.filter(id=worker.id).values('id').distinct()
	
		
   		
		for year in elenco:
    			single_data={}
    			single_data['nome'] = year['id']
    			single_data['data'] = year['data']
    			single_data['notareg'] = year['notareg']
    			single_data['nreg'] = year['nreg']
    			
    			dat = dat + [single_data]
     
	return render(request, 'popupadvance_importa.html', {'worker': worker, 'dat': dat})

def recupera_dati(ordine, notareg, nreg):
	
	import urllib2
	import pdfminer
	import cStringIO
	from pdfminer.pdfparser import PDFParser
	from pdfminer.pdfdocument import PDFDocument
	from pdfminer.pdfpage import PDFPage
	from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
	from pdfminer.pdfdevice import PDFDevice
	from pdfminer.layout import LAParams
	from pdfminer.converter import  TextConverter # , XMLConverter, HTMLConverter
	import re
	
	import wdb; wdb.set_trace()
	
	
	url = 'https://tradingonline.poste.it/tol/PDFServlet?numReg='
	
	percorso = ''
	testo = ''
	if nreg != "" and notareg != "":
		stringa = nreg.split(' ')
		url = url+stringa[1]+'/'+stringa[2]+'/'+str(int(stringa[3]))+'/'+str(int(stringa[4]))

	if ordine != "":
		stringa = ordine.split('/')
		if int(stringa[4]) == 0:
			stringa[4] = '1'
		url = url+stringa[1]+'/'+stringa[2]+'/'+str(int(stringa[3]))+'/'+str(int(stringa[4]))
	
	#scarica il file pdf
	#per l'header dovrebbe bastare solo la sezione 'Accept'
	hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Connection': 'keep-alive'}
	req = urllib2.Request(url, headers=hdr)
	f = urllib2.urlopen(req)

	# Cast to StringIO object
	convertito = cStringIO.StringIO(f.read())
	f.close()
	
	# Create a PDF parser object associated with the StringIO object
	#parser = PDFParser(convertito)
	
	# Create a PDF document object that stores the document structure
	#document = PDFDocument(parser)
	
	# Define parameters to the PDF device objet and create it
	rsrcmgr = PDFResourceManager()
	retstr = cStringIO.StringIO()
	codec = 'utf-8'
	laparams = LAParams()
	device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

	# Create a PDF interpreter object
	interpreter = PDFPageInterpreter(rsrcmgr, device)

	# Process each page contained in the document
	password = ""
	maxpages = 0
	caching = True
	pagenos = set()
	for page in PDFPage.get_pages(convertito,
                                  pagenos,
                                  maxpages=maxpages,
                                  password=password,
                                  caching=caching,
                                  check_extractable=True):
        	interpreter.process_page(page)

	device.close()

	out = retstr.getvalue()
		
	single_data={}
	
	#parse del file pdf
	if out.find('COMPRA')==-1:
    		single_data['tipo']= 2
	else:
    		single_data['tipo']=1
    		
    	
    	for i in a.split("\n"):
    		t=i.split()
    		if len(t):
    			if t[0] == 'NOTA':
        			single_data['nota'] = t[1]
    			elif t[0] == 'NREG':
        			single_data['nreg'] = i
    			elif t[0] == 'DATA':
        			single_data['data'] = t[2]
    			elif t[0] == 'COMMISSIONI':
        			single_data['costo'] = t[1]
    			elif t[0] == 'ALTRI':
        			single_data['imposta'] = t[4]
    			elif t[0] == 'Rateo':
        			single_data['rateo'] = t[2]
    			elif t[0] == 'Imposta':
        			single_data['imposta_dietimi'] = t[3]

	begin = a.find('CONTANTI')
	end = a.find('COMMISSIONI')

	t = a[begin:end]
	
	p = re.compile('[A-Z]*[.,\d]+')
	listat = p.findall(a[begin:end])
	q = float(listat[0].replace('.','').replace(',','.'))
	c = float(listat[3].replace('.','').replace(',','.'))
	single_data['quantity'] = int(q)
	single_data['costounitario'] = c/q
	
	#infine dobbiamo rintracciare il titolo e il gruppo di investimento
	tit = ''
	invest = ''
	if titolo.objects.filter(isin=tt[4]):
		tit = titolo.objects.filter(isin=listat[4])[0].id
		invest = transazione.objects.filter(titolo=tit)[0].invest.nome
	
	single_data['titolo'] = tit
	single_data['invest'] = invest

	
	return single_data

	
def return_popup_importa(request):
	#import wdb; wdb.set_trace()
	tipo = request.GET['id']
	ordine = request.POST['ordine']
	notareg = request.POST['notareg']
	nreg = request.POST['nreg']
	
	info = recupera_dati(ordine, notareg, nreg)
	
	#se è una nuova transazione
	if tipo == "new":
		p = transazione(data = info['data'] if info.has_key('data') else '',
			titolo = info['titolo'] if info.has_key('titolo') else '',
			invest = info['invest'] if info.has_key('invest') else '',
			quantity = info['quantity'] if info.has_key('quantity') else '',
			costounitario = info['costounitario'] if info.has_key('costounitario') else '',
			costo = info['costo'] if info.has_key('costo') else '',
			tipo = info['tipo'] if info.has_key('tipo') else '',
			imposta = info['imposta'] if info.has_key('imposta') else '',
			rateo = info['rateo'] if info.has_key('rateo') else '',
			imposta_dietimi = info['imposta_dietimi'] if info.has_key('imposta_dietimi') else '',
			notareg = info['notareg'] if info.has_key('notareg') else '',
			nreg = info['nreg'] if info.has_key('nreg') else '')
		p.save()
			
	
	#se si stratta di aggiornare una transazione esistente
	else:
		p = get_object_or_404(transazione, pk=request.GET['id'])
		p.posizione_id = request.POST['choice']
		p.save()

	return HttpResponseRedirect('/admin/movimenti/transazione/'+str(p.id))


