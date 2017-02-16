# coding=utf-8
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.exportimport import instruments


class ExportView(BrowserView):
    """
    """
    def __call__(self):

        import pdb; pdb.set_trace()
        translate = self.context.translate

        instrument = self.context.getInstrument()
        if not instrument:
            self.context.plone_utils.addPortalMessage(
                _("You must select an instrument"), 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        #exim = instrument.getDataInterface()
        #if not exim:
        #    self.context.plone_utils.addPortalMessage(
        #        _("Instrument has no data interface selected"), 'info')
        #    self.request.RESPONSE.redirect(self.context.absolute_url())
        #    return

        ## exim refers to filename in instruments/
        #if type(exim) == list:
        #    exim = exim[0]
        #exim = exim.lower()

        ## search instruments module for 'exim' module
        #if not instruments.getExim(exim):
        #    self.context.plone_utils.addPortalMessage(
        #        _("Instrument exporter not found"), 'error')
        #    self.request.RESPONSE.redirect(self.context.absolute_url())
        #    return

        tray = 1
        now = DateTime().strftime('%Y%m%d-%H%M')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        uc = getToolByName(self.context, 'uid_catalog')
        norm = getUtility(IIDNormalizer).normalize
        filename  = '%s-%s.csv'%(self.context.getId(),
                                 norm(instrument.getDataInterface()))
        listname  = '%s_%s_%s' %(self.context.getId(),
                                 norm(instrument.Title()), now)
        options = {'dilute_factor' : 1,
                   'method': 'F SO2 & T SO2'}
        for k,v in instrument.getDataInterfaceOptions():
            options[k] = v

        # for looking up "cup" number (= slot) of ARs
        parent_to_slot = {}
        layout = self.context.getLayout()
        for x in range(len(layout)):
            a_uid = layout[x]['analysis_uid']
            p_uid = uc(UID=a_uid)[0].getObject().aq_parent.UID()
            layout[x]['parent_uid'] = p_uid
            if not p_uid in parent_to_slot.keys():
                parent_to_slot[p_uid] = int(layout[x]['position'])

        # write rows, one per PARENT
        header = [listname, options['method']]
        rows = []
        rows.append(header)
        tmprows = []
        ARs_exported = []
        for x in range(len(layout)):
            # create batch header row
            c_uid = layout[x]['container_uid']
            p_uid = layout[x]['parent_uid']
            if p_uid in ARs_exported:
                continue
            cup = parent_to_slot[p_uid]
            tmprows.append([tray,
                            cup,
                            p_uid,
                            c_uid,
                            options['dilute_factor'],
                            ""])
            ARs_exported.append(p_uid)
        tmprows.sort(lambda a,b:cmp(a[1], b[1]))
        rows += tmprows

        ramdisk = StringIO()
        writer = csv.writer(ramdisk, delimiter=';')
        assert(writer)
        writer.writerows(rows)
        result = ramdisk.getvalue()
        ramdisk.close()

        #stream file to browser
        setheader = self.request.RESPONSE.setHeader
        setheader('Content-Length',len(result))
        setheader('Content-Type', 'text/comma-separated-values')
        setheader('Content-Disposition', 'inline; filename=%s' % filename)
        self.request.RESPONSE.write(result)
