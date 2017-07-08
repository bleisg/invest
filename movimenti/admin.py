# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db.models import Sum
#from decimal import Decimal

# Register your models here.

from .models import tipo 
from .models import titolo
from .models import tipo_transazione
from .models import investimento
from .models import transazione
from .models import quota
from .models import posizione

from django.db.models import Q

from django.contrib.admin.views.main import ChangeList



class titoloAdmin(admin.ModelAdmin):   
	readonly_fields = ('image_tag',)
	ordering = ['nome'] 
   	list_display = ('sigla','nome','isin',)
	list_filter = ('id_tipo',)
	search_fields = ['nome',]
	

	
class transazioneAdmin(admin.ModelAdmin):   
	# Indica il totale della transazione di acquisto o vendita; il valore è rispettivamente negativo o positivo.
	# Analogamente in caso di imposta o costi di commissione (negativo), oppure di dividendo (positivo) 
	def totale(self, obj):
		# 1: acquisto
		# 4: imposta statale 12.5% o 26%
		# 5: imposta di altro tipo
		# 6: carico del portafoglio in seguito ad operazione societaria
		if (obj.tipo_id == 1) or (obj.tipo_id == 4) or (obj.tipo_id == 5) or (obj.tipo_id == 6):
			return ("%.2f" % (-(obj.quantity or 0)*(obj.costounitario or 0)-(obj.costo or 0)-(obj.imposta or 0)-(obj.rateo or 0)+(obj.imposta_dietimi or 0))) 
		else:
	    		return ("%.2f" % ((obj.quantity or 0)*(obj.costounitario or 0)-(obj.costo or 0)-(obj.imposta or 0)+(obj.rateo or 0)-(obj.imposta_dietimi or 0))) 
	
	def show_link(self, obj):
		percorso = ''
		testo = ''
		if obj.nreg:
			stringa = obj.nreg.split(' ')
			percorso = 'https://tradingonline.poste.it/tol/PDFServlet?numReg='+stringa[1]+'/'+stringa[2]+'/'+str(int(stringa[3]))+'/'+str(int(stringa[4]))
		if obj.notareg:
			testo = 'Ord. ' + str(int(obj.notareg))
    		return '<a href="%s">%s</a>' % (percorso, testo)
	show_link.allow_tags = True
	
    	def save_model(self, request, obj, form, change):
		#import wdb; wdb.set_trace()
    		if request.POST.has_key('storedvalue'):
            		q = request.POST.copy()
            		if q['storedvalue']:	
	            		obj.posizione = posizione.objects.get(id=q['storedvalue'])
    		super(transazioneAdmin, self).save_model(request, obj, form, change)

	
	ordering = ['-data'] 
   	list_display = ('titolo','id','tipo','data','quantity','costounitario','totale','invest','show_link','posizione',)
	list_filter = ('tipo','invest','posizione_id',)
	search_fields = ['titolo__nome',]
	list_per_page = 40
	readonly_fields = ('posizione',)
	save_on_top = True
	
class posizioneAdmin(admin.ModelAdmin):
	def commissioni_totali(self,obj):
		return "%.2f" %  (transazione.objects.filter(posizione_id=obj.id).aggregate(Sum('costo'))['costo__sum'] or 0)
		
	def quantity(self,obj):
		q = transazione.calcoli.totale(obj.id)
		tot = 0
		for i in q:
			if i.tipo_id ==1 or  i.tipo_id == 6:
				tot=tot+i.quantity
			elif  i.tipo_id ==2  or i.tipo_id ==7  or i.tipo_id ==8:
				tot=tot-i.quantity
			
		return tot
	
	def gain(self,obj):
		q = transazione.calcoli.totale(obj.id)
		tot = 0
		for i in q:
			if i.tipo_id ==1 or  i.tipo_id == 6 or  i.tipo_id == 4 or  i.tipo_id == 5:
				tot=tot - (i.importo or 0) - (i.costo or 0) - (i.imposta or 0) - (i.rateo or 0) + (i.imposta_dietimi or 0)
			elif  i.tipo_id ==2  or i.tipo_id ==7  or i.tipo_id ==8 or i.tipo_id ==3:
				tot=tot + (i.importo or 0) - (i.costo or 0) - (i.imposta or 0) + (i.rateo or 0) - (i.imposta_dietimi or 0)
		return "%.2f" % tot
	
				
	list_filter = ('opened',)
	list_display = ('id', 'titolo', 'opened','commissioni_totali','quantity','gain',)




admin.site.register(tipo)
admin.site.register(tipo_transazione)
admin.site.register(investimento,)
admin.site.register(transazione,transazioneAdmin)
admin.site.register(quota)
admin.site.register(titolo,titoloAdmin)
admin.site.register(posizione,posizioneAdmin)
