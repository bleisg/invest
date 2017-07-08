# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from movimenti.models import investimento, transazione, titolo, tipo_transazione, tipo, posizione
from django.db.models import Sum, Count
import datetime


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
    			single_data['cu'] =  abs(float(tot) / float(single_data['quantity']))
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
	#import wdb; wdb.set_trace()
	worker = request.GET.get('id')
	dat = []
	single_data={}
	confronto = 'ciao'
	if worker != 'new':
		nuova=0
		elenco = transazione.objects.filter(id=worker)[0]
		single_data['nome'] = elenco.titolo
		single_data['data'] = elenco.data
		single_data['notareg'] = elenco.notareg
		single_data['nreg'] = elenco.nreg
		confronto = 'Acquisto ' if elenco.tipo_id == 1 else 'Vendita\\n'
		confronto = confronto + '\\n' + elenco.notareg + '\\n' + elenco.nreg + '\\n' + 'COSTO ' + str(elenco.costo) + '\\n' + 'IMPOSTA ' + str(elenco.imposta)
		confronto = confronto + '\\n' + 'DATA '+ str(datetime.datetime.strftime(elenco.data, "%d/%m/%Y")) + '\\n' + 'quantita ' + str(elenco.quantity) + '\\n' + 'costounitario ' + str(elenco.costounitario) + '\\n'


	return render(request, 'popupadvance_importa.html', {'worker': worker, 'dat': single_data, 'confronto' : confronto})


def recupera_dati(out):
	#import wdb; wdb.set_trace()

	single_data={}

	#parse
	if out.find('Acquisto')==-1:
		single_data['tipo']= 2
	else:
		single_data['tipo']=1


	for i in out.split("\n"):
		t=i.split()
		if len(t):
			if t[0] == 'NOTAREG':
				single_data['notareg'] = t[1]
			elif t[0] == 'NREG':
				single_data['nreg'] = t[0]+' '+t[1]+' '+t[2]+' '+t[3]+' '+t[4]
			elif t[0] == 'DATA':
				single_data['data'] = t[1]
			elif t[0] == 'COSTO':
				single_data['costo'] = t[1]
			elif t[0] == 'IMPOSTA':
				single_data['imposta'] = t[1]
			elif t[0] == 'rateo':
				single_data['rateo'] = t[1]
			elif t[0] == 'imposta_dietimi':
				single_data['imposta_dietimi'] = t[1]
			elif t[0] == 'quantita':
				single_data['quantity'] = t[1]
			elif t[0] == 'costounitario':
				single_data['costounitario'] = t[1]
			elif t[0] == 'isin':
				isin = t[1]

	#infine dobbiamo rintracciare il titolo e il gruppo di investimento
	#l'investimento viene determinato conoscendo una precedente transazione
	#con il medesimo titolo
	tit = ''
	invest = ''
	if titolo.objects.filter(isin=isin):
		tit = titolo.objects.filter(isin=isin)[0].id
		if transazione.objects.filter(titolo=tit):
			invest = transazione.objects.filter(titolo=tit)[0].invest.id
        #valutare il caso di transazione non correlata con nuovi investimenti
        #else

	#TODO
	#Valutare il caso eventuale di un nuovo isin non in archivio

	single_data['titolo'] = tit
	single_data['invest'] = invest


	return single_data


def return_popup_importa(request):
	#import wdb; wdb.set_trace()
	worker = request.GET['id']

	#insieme dei dati
	testo = request.POST['testoarea']

	info = recupera_dati(testo)

	#occorre inserire un controllo per i campi obbligatori titolo, invest, tipo_id (acquisto=1 o vendita=2)
	#che risultano necessari, ma possono presentarsi vuoti (soprattutto titolo e invest per nuovi titoli
	#non in database prima)
	if info['titolo'] and info['invest'] and info['tipo']:
		#In caso di nuova transazione:
		#occorre inserire un controllo per notareg e nreg se presenti già in database
		if worker == "new":
			if info['notareg'] and info['nreg'] and \
				(not (transazione.objects.filter(notareg=info['notareg']))) and \
				(not (transazione.objects.filter(nreg=info['nreg']))):

				p = transazione.objects.create(data = datetime.datetime.strptime(info['data'], "%d/%m/%Y") if info.has_key('data') else '',
					titolo_id = info['titolo'] if info.has_key('titolo') else '',
					invest_id = info['invest'] if info.has_key('invest') else '',
					quantity = float(info['quantity']) if info.has_key('quantity') else 0,
					costounitario = float(info['costounitario']) if info.has_key('costounitario') else 0,
					costo = float(info['costo']) if info.has_key('costo') else 0,
					tipo_id = info['tipo'] if info.has_key('tipo') else '',
					imposta = float(info['imposta']) if info.has_key('imposta') else 0,
					rateo = float(info['rateo']) if info.has_key('rateo') else 0,
					imposta_dietimi = float(info['imposta_dietimi']) if info.has_key('imposta_dietimi') else 0,
					notareg = info['notareg'] if info.has_key('notareg') else '',
					nreg = info['nreg'] if info.has_key('nreg') else '')
				return HttpResponseRedirect('/admin/movimenti/transazione/'+str(worker))
			else:
				#aprire pagina con errore in quanto o nreg o notareg già in database
				#return HttpResponseRedirect('/admin/errore.html')
				return render(request, 'errore.html', {'message' : 'Attenzione! NOTAREG e NREG già in database.'})
				#return HttpResponse('<script> alert("Attenzione! NOTAREG e NREG già in database."); </script>')

		#se si stratta di aggiornare una transazione esistente
		#verificare se i campi nreg, notareg e titolo coincidono; anzi sarebbe comodo evidenziare tra tutti i dati inseriti quelli
		#che non collimano, chiedendo all'utente cosa fare
		else:
			p = get_object_or_404(transazione, pk=request.GET['id'])
			# 1) può capitare di aggiornare solo i campi nreg e notareg che sono lasciati vuoti nella versione preliminare inserita
			#nel database. E' utile in tal caso proporre una pagina web che mostra le differenze e la richiesta di accettare
			#o rifuitare l'aggiornamento proposto
			if info['notareg'] and info['nreg']  and p.titolo_id == info['titolo'] and (not p.nreg) and  (not p.notareg):
				p.nreg = info['nreg']
				p.notareg  = info['notareg']
				p.titolo_id = info['titolo'] if info.has_key('titolo') else ''
				p.invest_id = info['invest'] if info.has_key('invest') else ''
				p.data = datetime.datetime.strptime(info['data'], "%d/%m/%Y") if info.has_key('data') else ''
				p.quantity = float(info['quantity']) if info.has_key('quantity') else 0
				p.costounitario = float(info['costounitario']) if info.has_key('costounitario') else 0
				p.costo = float(info['costo']) if info.has_key('costo') else 0
				p.tipo_id = info['tipo'] if info.has_key('tipo') else ''
				p.imposta = float(info['imposta']) if info.has_key('imposta') else 0
				p.rateo = float(info['rateo']) if info.has_key('rateo') else 0
				p.imposta_dietimi = float(info['imposta_dietimi']) if info.has_key('imposta_dietimi') else 0
				p.save()

			#2) può capitare invece di dover caricare altri campi (o magari corregerli), occorre quindi
			#che titoloid, notareg e nreg coincidano, prima di aggiornare tutti gli altri
			elif ((p.titolo_id == info['titolo']) and (p.notareg == info['notareg']) and (p.nreg == info['nreg'])):
				p.invest_id = info['invest'] if info.has_key('invest') else ''
				p.quantity = float(info['quantity']) if info.has_key('quantity') else 0
				p.data = datetime.datetime.strptime(info['data'], "%d/%m/%Y") if info.has_key('data') else ''
				p.costounitario = float(info['costounitario']) if info.has_key('costounitario') else 0
				p.costo = float(info['costo']) if info.has_key('costo') else 0
				p.tipo_id = info['tipo'] if info.has_key('tipo') else ''
				p.imposta = float(info['imposta']) if info.has_key('imposta') else 0
				p.rateo = float(info['rateo']) if info.has_key('rateo') else 0
				p.imposta_dietimi = float(info['imposta_dietimi']) if info.has_key('imposta_dietimi') else 0
				p.save()

	#return HttpResponseRedirect('/admin/movimenti/transazione/'+str(worker))
	#return HttpResponse("<!DOCTYPE html> <html> <body> <script> window.onbeforeunload = function(){ window.open('','_self').location.reload(true); window.open('','_self').close(); }; </script> </body> </html>")
	return HttpResponse('<script type="text/javascript">window.close(); window.opener.parent.location.href = "/" ; </script>')
	#return HttpResponse('<script type="text/javascript">window.close(); window.opener.parent.location.reload() ; </script>')

	return risposta


def ajax_query(request):
    if request.is_ajax() and request.method == 'POST':
        try:
        	chiave = request.POST['key']
        	tit=''
        	invest=''
        	if chiave == 'titolo':
        		isin = request.POST['isin']
        		if titolo.objects.filter(isin=isin):
					tit = titolo.objects.filter(isin=isin)[0].id
					if transazione.objects.filter(titolo=tit):
						invest = transazione.objects.filter(titolo=tit)[0].invest.id


        except KeyError:
            return HttpResponse('Error') # incorrect post

        return HttpResponse(str(score))
    else:
        raise Http404
