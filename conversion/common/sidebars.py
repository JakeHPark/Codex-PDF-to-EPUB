"""Find marginal prose blocks independently of font names and page numbers.

Geometry finds review candidates; different typography supports classification.
Callers must exclude captured object labels, captions and headings beforehand.
"""
import collections,statistics,re

def find_marginal_blocks(lines, prose_ids, minimum_main_width=240, maximum_sidebar_width=175, gutter=8):
    blocks=collections.defaultdict(list)
    for line in lines:
        blocks[line['id'].rsplit('-',1)[0]].append(line)
    main=[line for line in lines if line['id'] in prose_ids and line['box'][2]-line['box'][0]>minimum_main_width]
    findings=[]
    def size(group):
        return statistics.median(span['size'] for line in group for span in line['spans'])
    def family(group):
        weights=collections.Counter()
        for line in group:
            for span in line['spans']:
                name=re.sub(r'[-_](?:Roman|Regular|Bold|Italic|Oblique).*$', '', span['font'])
                weights[name]+=max(1,len(span.get('text','')))
        return weights.most_common(1)[0][0]
    for block, group in blocks.items():
        box=[min(line['box'][0] for line in group),min(line['box'][1] for line in group),max(line['box'][2] for line in group),max(line['box'][3] for line in group)]
        if len(group)<2 or box[2]-box[0]>maximum_sidebar_width:continue
        neighbors=[line for line in main if min(box[3],line['box'][3])>max(box[1],line['box'][1]) and (box[2]+gutter<line['box'][0] or box[0]>line['box'][2]+gutter)]
        if not neighbors:continue
        distinctive=size(group)<size(neighbors)-.25 or family(group)!=family(neighbors)
        findings.append(dict(block=block,line_ids=[line['id'] for line in group],box=box,neighbor_ids=[line['id'] for line in neighbors],distinctive_typography=distinctive,text=' '.join(line['text'] for line in group)))
    return findings
