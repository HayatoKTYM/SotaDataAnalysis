import sys
import os
import glob
import cgi

PATH = '/Volumes/Samsung_T5/prj-woz/data'
wav_files = sorted(glob.glob(os.path.join(PATH,'mix_wav/*wav')))
mp4_files = sorted(glob.glob(os.path.join(PATH,'mp4/*mp4')))
label_files = sorted(glob.glob(os.path.join(PATH,'text/*txt')))

os.makedirs(os.path.join(PATH,'ELAN'),exist_ok=True)

for i in range(len(label_files)):
    name = os.path.basename(label_files[i]).split('.')[0]
    #wav_file = wav_files[i]
    #avi_file =mp4_files[i]
    wav_file = os.path.join(PATH,'mix_wav') + '/' + name + '.mix.wav'
    avi_file = os.path.join(PATH,'mp4') + '/' + name + '.mp4'
    label_file = label_files[i]
    template_file = '/Users/hayato/Desktop/WOZ_katayama/ELAN_data/template.eaf'

    tier_list = []
    tier_dict = {}
    ts_list = []


    with open(label_file, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            #tier, _, start, end, dur, _ = line.rstrip().split('\t')
            tier, type , start, end ,  = line.rstrip().split(',')
            type = cgi.escape(type)
            if not tier in tier_list:
                tier_list.append(tier)
                tier_dict[tier] = []
            #a = [len(ts_list) + 1, len(ts_list) + 2]
            a = [len(ts_list) + 1, len(ts_list) + 2 , type]
            tier_dict[tier].append(a)
            ts_list.extend([int(float(start)), int(float(end))])


    ts_lines = ''
    for i, ts in enumerate(ts_list):
        ts_lines += '<TIME_SLOT TIME_SLOT_ID="ts%d" TIME_VALUE="%d"/>\n' % (i + 1, ts)
    # print ts_lines

    tier_lines = ''
    a_count = 0
    for tier in tier_list:
        # print tier
        a_lines = ''
        for a in tier_dict[tier]:
            a_lines += """\t<ANNOTATION>
                <ALIGNABLE_ANNOTATION ANNOTATION_ID="a%d" TIME_SLOT_REF1="ts%d" TIME_SLOT_REF2="ts%d">
                    <ANNOTATION_VALUE>%s</ANNOTATION_VALUE>
                </ALIGNABLE_ANNOTATION>
            </ANNOTATION>
    """ % (a_count + 1, a[0], a[1],a[2])
            a_count += 1
        tier_lines += ('<TIER DEFAULT_LOCALE="us" LINGUISTIC_TYPE_REF="default" TIER_ID="%s">\n' % (tier)) + a_lines + '</TIER>\n'

    # print tier_lines
    content = ''
    with open(template_file, 'r') as f:
        content = f.readlines()
    content = ''.join(content)

    content = content.replace('__MEDIA_DESCRIPTOR__',
                              '<MEDIA_DESCRIPTOR MEDIA_URL="file://%s" MIME_TYPE="audio/x-wav" RELATIVE_MEDIA_URL="%s"/>' % (os.path.abspath(wav_file), wav_file),1)
    content = content.replace('__MEDIA_DESCRIPTOR__',
                                '<MEDIA_DESCRIPTOR MEDIA_URL="file://%s" MIME_TYPE="video/*" RELATIVE_MEDIA_URL="%s"/>' % (os.path.abspath(avi_file), avi_file),1)
    content = content.replace('__LAST_USED_ANNOTATION_ID__',
                              '<PROPERTY NAME="lastUsedAnnotationId">%d</PROPERTY>' % (a_count))
    content = content.replace('__TIME_SLOT__', ts_lines)
    content = content.replace('__TIER__', tier_lines)

    output = label_file.replace('/text','/ELAN').replace('.txt','.eaf')
    print(output)
    
    with open(output,"w") as f:
        f.write(content)
