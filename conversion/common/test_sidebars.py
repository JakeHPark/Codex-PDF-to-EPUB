import unittest
from sidebars import find_marginal_blocks

def line(block,n,x,width,y,text,size=10.5,font='Body'):
    return dict(id=f'1-{block}-{n}',box=[x,y,x+width,y+10],text=text,spans=[dict(size=size,font=font)])

class SidebarTests(unittest.TestCase):
    def test_separate_stream_at_multiple_font_sizes_and_both_margins(self):
        for left in [True,False]:
            for size in [8,9.5]:
                main=[line(1,n,224 if left else 80,330,100+n*14,'Main prose') for n in range(6)]
                note=[line(2,n,80 if left else 424,125,110+n*12,'Sidebar prose',size) for n in range(4)]
                found=find_marginal_blocks(main+note,{l['id'] for l in main})
                self.assertEqual(len(found),1);self.assertTrue(found[0]['distinctive_typography']);self.assertEqual(len(found[0]['line_ids']),4)
    def test_inset_quotation_overlaps_main_column_and_is_not_marginal(self):
        main=[line(1,n,80,330,100+n*14,'Main prose') for n in range(6)]
        quote=[line(2,n,110,125,110+n*12,'Inset quote',9.5) for n in range(4)]
        self.assertEqual(find_marginal_blocks(main+quote,{l['id'] for l in main}),[])
    def test_italic_or_bold_prose_uses_the_same_font_family(self):
        main=[line(1,n,224,330,100+n*14,'Main prose',font='Berling-Italic') for n in range(6)]
        steps=[line(2,n,80,125,110+n*12,'Observation heading',font='Berling-Roman') for n in range(4)]
        self.assertFalse(find_marginal_blocks(main+steps,{l['id'] for l in main})[0]['distinctive_typography'])
    def test_tiny_marker_font_does_not_define_main_prose_family(self):
        main=[line(1,n,224,330,100+n*14,'Main prose',font='Berling-Roman') for n in range(6)]
        for l in main:l['spans']=[dict(font='Marker-Bold',size=10.5,text='c. '),dict(font='Berling-Roman',size=10.5,text='Long ordinary prose description')]
        steps=[line(2,n,80,125,110+n*12,'Observation heading',font='Berling-Roman') for n in range(4)]
        self.assertFalse(find_marginal_blocks(main+steps,{l['id'] for l in main})[0]['distinctive_typography'])
    def test_narrow_instruction_is_only_a_review_candidate(self):
        main=[line(1,n,224,330,100+n*14,'Main prose') for n in range(6)]
        steps=[line(2,n,80,125,110+n*12,'Exercise step') for n in range(4)]
        found=find_marginal_blocks(main+steps,{l['id'] for l in main})
        self.assertFalse(found[0]['distinctive_typography'])

if __name__=='__main__':unittest.main()
