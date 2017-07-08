# -*- coding: utf-8 -*-
from django.db import models
from datetime import date
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from django.db.models import Q
from django.db.models import Sum, Min, Max

from django.db.models.signals import post_save
from django.dispatch import receiver
import webbrowser
from django.http import HttpResponse, HttpResponseRedirect


#
#identifica il tipo di titolo: tds, tds euro, azione, etf...
class tipo(models.Model):
	nome = models.CharField(max_length=20)
	descrizione = models.TextField(blank=True)
	tassazione = models.DecimalField(max_digits=5, decimal_places=2)
	def __unicode__(self):
		return self.nome

	class Meta:
		verbose_name_plural = "Tipologia dei titoli"
		ordering = ['nome']

# titolo trattato
class titolo(models.Model):
	def acronimo(self):
		return selfsigla.partition(":")[2]

	def image_tag(self):
    		return u'<img src="%s" /> <img src="%s" /> <img src="%s" />' % (self.storico1m, self.storico6m, self.storico2a,)

	image_tag.short_description = 'Image'
	image_tag.allow_tags = True

	nome = models.CharField(max_length=50)
	#sigla secondo lo standard advfn, es. BIT:UCG
	sigla = models.CharField(max_length=50)
	descr = models.CharField(max_length=100, blank=True, verbose_name="Descrizione")
	id_tipo = models.ForeignKey(tipo, verbose_name="Tipologia")
	emittente = models.CharField(max_length=30,default="idem")
	mercato = models.CharField(max_length=30)
	isin = models.CharField(max_length=15, unique=True)
	dividendo = models.BooleanField()
	#seguono link a immagini advfn per lo storico a 1 mese, 6 mesi e 2 anni
	storico1m = models.URLField(blank=True,max_length=250, default="http://it.advfn.com/p.php?pid=staticchart&s=BIT%5EIES&t=37&p=2&dm=0&vol=0&width=280&height=200&min_pre=0&min_after=0")
	storico6m = models.URLField(blank=True,max_length=250, default="http://it.advfn.com/p.php?pid=staticchart&s=BIT%5EIES&t=37&p=4&dm=0&vol=0&width=280&height=200&min_pre=0&min_after=0")
	storico2a = models.URLField(blank=True,max_length=250, default="http://it.advfn.com/p.php?pid=staticchart&s=BIT%5EIES&t=37&p=7&dm=0&vol=0&width=280&height=200&min_pre=0&min_after=0")
	note = models.TextField(blank=True)

	def __unicode__(self):
		return self.nome


	class Meta:
		verbose_name_plural = "Titoli"
		ordering = ['nome']

class tipo_transazione(models.Model):
	#tipo_transazione_id
	# 1: acquisto
	# 2: vendita
	# 3: dividendo
	# 4: imposta statale 12.5% o 26%
	# 5: imposta di altro tipo
	# 6: carico del portafoglio in seguito ad operazione societaria
	# 7: scarico
	# 8: rimborso
	nome = models.CharField(max_length=50)
	def __unicode__(self):
		return self.nome

	class Meta:
		verbose_name_plural = "Tipo transazione"

#Alcune transazioni, di diverso tipo, possono essere raggruppate in investimenti,
#dei quali possono essere calcolate diverse caratteristiche, come rendimento, durata,....
class investimento(models.Model):
	nome = models.CharField(max_length=30)
	descr = models.TextField(blank=True,verbose_name="Descrizione")
	#target
	#rischio
	def __unicode__(self):
		return self.nome

	class Meta:
		verbose_name_plural = "Investimenti"

#A differenza degli investimenti, le posizioni sono relative all'ingresso in un solo titolo (acquisti di un'azione)
#e vengono chiuse quando si esce completamente da quel titolo (vendita di tutta la quantità)
#Si possono avere differenti posizioni per lo stesso titolo, aperte in tempi diversi.
#Per uno stesso titolo, si ha apertura di una nuova posizione quando tutte le precedenti posizioni
#per quel titolo sono chiuse.
class posizione(models.Model):
	opened = models.BooleanField(default=True)
	titolo = models.ForeignKey(titolo)
	def __unicode__(self):
		return str(self.id) + " - " + str(self.opened) + " - " + self.titolo.nome


class transazioneManager(models.Manager):
	def totale(self, posizione):
        	from django.db import connection
        	cursor = connection.cursor()
        	cursor.execute("""
         			SELECT id, tipo_id, SUM(IFNULL(quantity,0)) , SUM(IFNULL(quantity*costounitario,0)), SUM(IFNULL(rateo,0)),
            			SUM(IFNULL(imposta_dietimi,0)), SUM(IFNULL(imposta,0)), SUM(IFNULL(costo,0)), COUNT(*)
            			FROM movimenti_transazione
            			WHERE posizione_id = %s
            			GROUP BY tipo_id
            			""",[posizione])
        	result_list = []
        	for row in cursor.fetchall():
            		p = self.model(tipo_id=row[1], quantity=row[2],  rateo=row[4], imposta_dietimi=row[5], imposta=row[6], costo=row[7])
            		p.num_responses = row[8]
            		p.importo = row[3]
            		result_list.append(p)
        	return result_list


	def durata(self, posizione):
		result_list = []
        	inizio=transazione.objects.filter(posizione_id=posizione).exclude(Q(tipo = 3) | Q(tipo = 4) | Q(tipo = 5)).aggregate(Min('data'))['data__min']
        	fine=transazione.objects.filter(posizione_id=posizione).exclude(Q(tipo = 3) | Q(tipo = 4) | Q(tipo = 5)).aggregate(Max('data'))['data__max']
        	delta = fine-inizio
        	result_list.append(inizio)
        	result_list.append(fine)
        	result_list.append(delta.days)
        	return result_list


class transazione(models.Model):
	data = models.DateField(_("Date"), default=date.today)
	titolo = models.ForeignKey(titolo)
	quantity = models.IntegerField(blank=True, null=True, verbose_name="Quantità")
	#quantity = models.DecimalField(max_digits=10, decimal_places=3,blank=True, null=True, verbose_name="Quantità")
	costounitario = models.DecimalField(max_digits=15, decimal_places=9,blank=True, null=True, verbose_name="Costo unitario")
	tipo = models.ForeignKey(tipo_transazione)
	costo = models.DecimalField(max_digits=10, decimal_places=5,blank=True, null=True, help_text="Importo sempre positivo. Nello scarico indicare un importo negativo per compensazione.<BR>Si noti che scaricando una posizione per subentrarne un'altra con un carico, la vecchia posizione prevede l'annullamento dei costi,<BR>in modo che i vecchi costi vengano caricati nella nuova posizione.")
	imposta = models.DecimalField(max_digits=10, decimal_places=5,blank=True, null=True, help_text="Nel caso di dividendo, indicare l'imposta automaticamente trattenuta<BR>mentre nel campo costo il valore intero")
	rateo = models.DecimalField(max_digits=10, decimal_places=5,blank=True,null=True)
	imposta_dietimi = models.DecimalField(max_digits=10, decimal_places=5,blank=True,null=True, verbose_name="Imposta sui dietimi")
	# Raggruppamento delle transazioni in investimenti
	invest = models.ForeignKey(investimento, verbose_name="Investimento")
	# Un tipo di raggruppamento diverso degli investimenti per attuare indagini e analisi
	tag = models.CharField(max_length=30,blank=True)
	note = models.TextField(blank=True)
	#Riferimento all'ordine TOL
	notareg = models.CharField(max_length=40,blank=True)
	nreg = models.CharField(max_length=40,blank=True)
	#Del valore di questo campo si occupa il metodo save()
	posizione = models.ForeignKey(posizione, null=True)

	objects = models.Manager() #default manager
	calcoli = transazioneManager()



	def importo(self,obj):
		return quantity*costounitario

	def __unicode__(self):
		return 	u"%s di '%s' in data %s " % (self.tipo, self.titolo, self.data.strftime('%d/%m/%Y'))

	class Meta:
		verbose_name_plural = "Transazioni"
		ordering = ['data']





    	#post_save.connect(abbina_posizione, sender=transazione, dispatch_uid="abbina_transazione_posizione")

	def save(self, *args, **kwargs):
		#La funzione .save che andiamo a sscrivere serve ad automatizzare il processo di
		#aggiornamento e/o creazione delle posizioni in base alla transazione che si sta
		#salvando

		#import pdb; pdb.set_trace()
		#import IPython; IPython.embed()
		#import wdb; wdb.set_trace()


		#Nello scarico di un titolo, viene effettuato il controllo che il costo di commissione sia negativo
		if self.tipo.id==7 and self.costo>0:
			self.costo=-self.costo


		#Consideriamo il caso che la transazione sia dividendo/cedola, imposte e altre imposte;
		#allora dobbiamo tenere conto del fatto che non si deve aprire nessuna nuova posizione:
		#bisogna individuare posizioni chiuse o aperte da abbinare alla transazione
		#IN QUESTA VERSIONE PRELIMINARE NON VIENE CONSIDERATO IL CASO DI NUOVA TRANSAZIONE
		#CON POSIZIONI CHIUSE E QUINDI DA IDENTIFICARE
		if (self.tipo.id==3) or (self.tipo.id==4) or (self.tipo.id==5):
			pos = posizione.objects.filter(titolo=self.titolo)
			pos_aperta = pos.filter(opened=True)
			if pos_aperta:
				self.posizione = pos_aperta[0]
			#else:
				#non esistendo una posizione aperta, si dovrebbe determinare la posizione
				#chiusa da abbinare alla transazione
				#L'esecuzione viene trasferita ad una finestra popup di interrogazione
			return super(transazione, self).save(*args, **kwargs)


		#Per le altre operazioni, si tratta di creare la posizione o eventualmente aggiornarla
		#Transazione non presente in db, ovvero nuova
		if (not self.posizione) and (not self.pk):
			#Occorre considerare i caratteristiche di apertura di una nuova
			#posizione o aggiornamento di una già aperta

			#Caso di apertura nuova posizione
			pos = posizione.objects.filter(titolo=self.titolo)
			if (not pos) or (not pos.filter(opened=True)):
				pos_nuova = posizione.objects.create(titolo_id=self.titolo.id, opened=True)
				self.posizione = pos_nuova

			#Caso di aggiornamento  posizione aperta
			else:
				pos_aperta = pos.filter(opened=True)
				self.posizione = pos_aperta[0]
				#La tabella posizione contiene, oltre al titolo, solo il campo opened
				#per cui è da aggiornare solo quello. Il campo viene impostato a False
				#ovvero posizione chiusa, quando la quantità della posizione aperta si
				#porta a zero
				q = transazione.objects.filter(posizione_id=pos_aperta[0].id)
				quant_caricata = (q.filter(Q(tipo = 1) | Q(tipo = 6)).aggregate(Sum('quantity'))['quantity__sum'] or 0)
				quant_scaricata =  (q.filter(Q(tipo = 2) | Q(tipo = 7) | Q(tipo = 8)).aggregate(Sum('quantity'))['quantity__sum'] or 0)
				#Nel caso la presente transazione sia una vendita, uno scarico oppure un rimborso, se la quantità in archivio,
				#tolta quella della presente transazione non ancora caricata, si annulla, vuol dire che transazione si chiude
				if (self.tipo.id==2 or self.tipo.id==7 or self.tipo.id==8) and (quant_caricata - quant_scaricata - self.quantity)==0:
					pos_aperta.update(opened=False)
				#Nel caso in cui la transazione sia un acquisto o un carico, nulla cambia nella posizione che rimane aperta

				#Se l'espressione "quant_caricata - quant_scaricata - self.quantity" è negativa bisogna segnalarlo
        		#if (quant_caricata - quant_scaricata - self.quantity)<0:
        			#SEGNALARE ERRORE

		#Aggiornamento di una transazione già in db
		#L'unica variazione che può interessare è quella relativa al  campo opened
		#che è collegato a quantity e tipo; quindi conosciuta la quantity precedente che andiamo
		#a variare, in funzione della nuova quantity andiamo a variare opened
		#RICORDA ci interessa solo opened perchè questa funzione .save serve ad automatizzare il processo di
		#aggiornamento e/o creazione delle posizioni in base alla transazione che si sta
		#salvando
		else:
			#Occorre considerare se sia stata scelta o meno una posizione
			#nella transazione che si sta aggiornando

			trans = transazione.objects.get(id=self.id)
			old_quantity = trans.quantity
			old_tipo = trans.tipo
			old_posizione = self.posizione

			#Non era stata specificata alcuna posizione precedentemente
			if not old_posizione:
				#Caso di posizione NON specificata, ma non ne esistono di aperte per il titolo in questione
				pos = posizione.objects.filter(titolo=self.titolo)
				if (not pos) or (not pos.filter(opened=True)):
					pos_nuova = posizione.objects.create(titolo_id=self.titolo.id, opened=True)
					self.posizione = pos_nuova
					#Caso di posizione NON specificata, ma ne esistono aperte per il titolo in questione
				else:
					pos_aperta = pos.filter(opened=True)
					self.posizione = pos_aperta[0]
					#La tabella posizione contiene, oltre al titolo, solo il campo opened
					#per cui è da aggiornare solo quello. Il campo viene impostato a False
					#ovvero posizione chiusa, quando la quantità della posizione aperta si
					#porta a zero
					q = transazione.objects.filter(posizione_id=pos_aperta[0].id)
					quant_caricata = (q.filter(Q(tipo = 1) | Q(tipo = 6)).aggregate(Sum('quantity'))['quantity__sum']  or 0)
					quant_scaricata = (q.filter(Q(tipo = 2) | Q(tipo = 7) | Q(tipo = 8)).aggregate(Sum('quantity'))['quantity__sum'] or 0)
					#Nel caso la presente transazione sia una vendita, uno scarico oppure un rimborso, se la quantità in archivio,
					#tolta quella della presente transazione non ancora caricata, si annulla, vuol dire che transazione si chiude
					if (self.tipo.id==2 or self.tipo.id==7 or self.tipo.id==8) and (quant_caricata - quant_scaricata - self.quantity)==0:
						pos_aperta.update(opened=False)
					#Nel caso in cui la transazione sia un acquisto o un carico, nulla cambia nella posizione che rimane aperta

					#Se l'espressione "quant_caricata - quant_scaricata - self.quantity" è negativa bisogna segnalarlo
        			#if (quant_caricata - quant_scaricata - self.quantity)<0:
        				#SEGNALARE ERRORE

			#Se la posizione è stata assegnata e a variare è la quantità o il tipo di transazione, allora forse si tratta
			#di chiudere una posizione aperta o di aprire una posizione chiusa
			elif old_quantity!=self.quantity or old_tipo!=self.tipo:
				pos = posizione.objects.get(id=old_posizione.id)
				q = transazione.objects.filter(posizione_id=old_posizione.id)
				quant_caricata = (q.filter(Q(tipo = 1) | Q(tipo = 6)).exclude(id=self.id).aggregate(Sum('quantity'))['quantity__sum']  or 0)
				quant_scaricata = (q.filter(Q(tipo = 2) | Q(tipo = 7) | Q(tipo = 8)).exclude(id=self.id).aggregate(Sum('quantity'))['quantity__sum'] or 0)

				#Se la posizione esiste ed era aperta, allora se si tratta di una transazione di vendita o scarico, bisogna vedere
				#cosa succede alla quantità complessiva della transazione al netto della nuova quantità, a prescindere di quale quantità
				#era specificata precedentemente.
				if pos.opened==True and ((self.tipo.id == 2) or (self.tipo.id == 7) or (self.tipo.id == 8)) and (quant_caricata - quant_scaricata - self.quantity)==0:
					pos.update(opened=False)
				if pos.opened==True and ((self.tipo.id == 1) or (self.tipo.id == 6)) and (quant_caricata - quant_scaricata + self.quantity)==0:
					pos.update(opened=False)
				#Se la posizione era chiusa, allora se si tratta di una transazione di carico o acquisto, bisogna vedere
				#la quantità complessiva algebrica, considerata la nuova operazione
				if pos.opened==False and ((self.tipo.id == 1) or (self.tipo.id == 6)) and (quant_caricata - quant_scaricata + self.quantity)>0:
					pos.update(opened=True)
				if pos.opened==False and ((self.tipo.id == 2) or (self.tipo.id == 7) or (self.tipo.id == 8)) and (quant_caricata - quant_scaricata - self.quantity)>0:
					pos.update(opened=True)
				#se è negativa bisogna segnalarlo
        		#elif (quant_caricata - quant_scaricata - self.quantity)<0:
        			#SEGNALARE ERRORE

		super(transazione, self).save(*args, **kwargs)



class quota(models.Model):
	data = models.DateField(_("Date"), default=date.today)
	nome = models.CharField(max_length=30)
	#tipo = deposito cash, prelievo cash
	tipo_quota_scelta = (
		('DEP','Deposito cash'),
		('PRE','Prelievo cash'),
    	)
    	tipo = models.CharField(max_length=3,
                                      choices = tipo_quota_scelta,
                                      default = 'DEP')

	quantita = models.DecimalField(max_digits=10, decimal_places=5, verbose_name="Quantità")
	note = models.TextField(blank=True)

	class Meta:
		verbose_name_plural = "Quote di capitale"
		ordering = ['data']


@receiver(post_save, sender=transazione)
def abbina_posizione(sender, instance, **kwargs):
     	#import wdb; wdb.set_trace()
     	import urllib
    	if not instance.posizione:
    		f = { 'id' : instance.id, 'attuale' : instance.posizione}
    		data = urllib.urlencode(f)
    		webbrowser.open('http://localhost:8000/popup/?'+data,0)
    	return False
