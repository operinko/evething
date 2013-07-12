import gzip
import json

from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    
from thing.forms import UploadSkillPlanForm
from thing.models import *
from thing.stuff import *


# ---------------------------------------------------------------------------
# List all skillplans
@login_required
def skillplan(request):
    return render_page(
        'thing/skillplan.html',
        {
            'skillplans': SkillPlan.objects.filter(user=request.user).order_by('id'),
            'visibilities': SkillPlan.VISIBILITY_CHOICES,
        },
        request,
    )


# ---------------------------------------------------------------------------
# Create a skillplan
@login_required
def skillplan_edit(request, skillplan_id):

    if skillplan_id.isdigit():
        try:
            skillplan = SkillPlan.objects.get(user=request.user, id=skillplan_id)
        
        except SkillPlan.DoesNotExist:
            request.session['message_type'] = 'error'
            request.session['message'] = 'You do not own that skill plan!'
                

        # Init the global skill list
        skill_list           = OrderedDict()
        current_market_group = None

        skills = Skill.objects.filter(item__market_group__isnull=False)
        skills = skills.select_related('item__market_group')
        skills = skills.order_by('item__market_group__name', 'item__name')
        
        for skill in skills:
            market_group = skill.item.market_group
            if market_group != current_market_group:
                current_market_group = market_group
                skill_list[current_market_group] = []

            # TODO : add char skill level for plan creation
            # maybe create a list with "allowed skill"
            # and "not reached prerequisite" skills
            
            skill_list[current_market_group].append(skill)
        
        characters = Character.objects.filter(
            apikeys__user=request.user,
        ).select_related(
            'config',
            'details',
        ).distinct()

        try:
            selected_char = characters.get(id=request.GET.get('character'))
        except Character.DoesNotExist:
            selected_char = False
        
        skillplan_details = _skillplan_list(request, skillplan, selected_char)
        #print(', '.join(skill_list))
        return render_page(
            'thing/skillplan_entries.html',
            {   
                'skillplan'         : skillplan,
                'skill_list'        : skill_list,
                'show_trained'      : skillplan_details.get('show_trained'),
                'implants'          : skillplan_details.get('implants'),
                'char'              : skillplan_details.get('character'),
                'entries'           : skillplan_details.get('entries'),
                'total_remaining'   : skillplan_details.get('total_remaining'),
                'characters'        : characters,
                'selected_character': selected_char
            }
            ,
            request,
        )

    else:
        redirect('thing.views.skillplan')


# ---------------------------------------------------------------------------
# Add a given skill & prerequisites
@login_required
def skillplan_add_skill(request):
    """
    Add skill into a given plan
    this function will add the prerequisites too and return
    the whole list (in json) of the skills to add.
    
    POST:   skillplan_id : id of the plan
            skill_id : skill to add 
    """
    
    if request.is_ajax():
        skill_id = request.POST.get('skill_id', '')
        skillplan_id = request.POST.get('skillplan_id', '')
        
        if skill_id.isdigit() and skillplan_id.isdigit():
            
            skill = Skill.objects.get(item__id=skill_id)
            skill_json = OrderedDict()
            skill_json[skill.item.id] = {}
            skill_json[skill.item.id]['skillname'] = skill.item.name
            skill_json[skill.item.id]['skill_id']  = skill.item.id
            
            
            return HttpResponse(json.dumps(skill_json), status=200)
        
        else:
            return HttpResponse(content='Cannot add the skill : no skill or no skillplan provided', status=500)       
    else:
        return HttpResponse(content='test', status=403)

    
    
     
# ---------------------------------------------------------------------------
# Import a skillplan
@login_required
def skillplan_import_emp(request):
    if request.method == 'POST':
        form = UploadSkillPlanForm(request.POST, request.FILES)
        if form.is_valid():
            _handle_skillplan_upload(request)
            return redirect('thing.views.skillplan')
        else:
            request.session['message_type'] = 'error'
            request.session['message'] = 'Form validation failed!'
    else:
        request.session['message_type'] = 'error'
        request.session['message'] = "That doesn't look like a POST request!"

    return redirect('thing.views.skillplan')

# ---------------------------------------------------------------------------
# Create a skillplan
def skillplan_add(request):

    skillplan = SkillPlan.objects.create(
        user=request.user,
        name=request.POST['name'],
        visibility=request.POST['visibility'],
    )
    
    skillplan.save()
    
    return redirect('thing.views.skillplan')
    
# ---------------------------------------------------------------------------
# Export Skillplan
def skillplan_export(request, skillplan_id):
    # path = os.expanduser('~/files/pdf/')
    # f = open(path+filename, "r")
    # response = HttpResponse(FileWrapper(f), content_type='application/x-gzip')
    # response ['Content-Disposition'] = 'attachment; filename=yourFile.emp'
    # f.close()
    return response

# ---------------------------------------------------------------------------
# Delete a skillplan
@login_required
def skillplan_delete(request):
    skillplan_id = request.POST.get('skillplan_id', '')
    if skillplan_id.isdigit():
        try:
            skillplan = SkillPlan.objects.get(user=request.user, id=skillplan_id)
        
        except SkillPlan.DoesNotExist:
            request.session['message_type'] = 'error'
            request.session['message'] = 'You do not own that skill plan!'
        
        else:
            request.session['message_type'] = 'success'
            request.session['message'] = 'Skill plan "%s" deleted successfully!' % (skillplan.name)
            
            # Delete all of the random things for this skillplan
            entries = SPEntry.objects.filter(skill_plan=skillplan)
            SPRemap.objects.filter(pk__in=[e.sp_remap_id for e in entries if e.sp_remap_id]).delete()
            SPSkill.objects.filter(pk__in=[e.sp_skill_id for e in entries if e.sp_skill_id]).delete()
            entries.delete()
            skillplan.delete()

    else:
        request.session['message_type'] = 'error'
        request.session['message'] = 'You seem to be doing silly things, stop that.'

    return redirect('thing.views.skillplan')


# ---------------------------------------------------------------------------
# Edit a skillplan
@login_required
def skillplan_info_edit(request):
    skillplan_id = request.POST.get('skillplan_id', '')
    if skillplan_id.isdigit():
        try:
            skillplan = SkillPlan.objects.get(user=request.user, id=skillplan_id)
        
        except SkillPlan.DoesNotExist:
            request.session['message_type'] = 'error'
            request.session['message'] = 'You do not own that skill plan!'
        
        else:
            skillplan.name = request.POST['name']
            skillplan.visibility = request.POST['visibility']
            skillplan.save()

            request.session['message_type'] = 'success'
            request.session['message'] = 'Skill plan "%s" edited successfully!' % (skillplan.name)

    else:
        request.session['message_type'] = 'error'
        request.session['message'] = 'You seem to be doing silly things, stop that.'

    return redirect('thing.views.skillplan')

# ---------------------------------------------------------------------------
def _skillplan_list(request, skillplan, character = False):
    tt = TimerThing('skillplan_list')

    utcnow = datetime.datetime.utcnow()

    # Check our GET variables
    implants = request.GET.get('implants', '')
    if implants.isdigit() and 0 <= int(implants) <= 5:
        implants = int(implants)
    else:
        implants = 0

    show_trained = ('show_trained' in request.GET)

    tt.add_time('init')

    # Init some stuff to have no errors
    learned = {}
    training_skill = None
    # Try retrieving learned data from cache
    if character:
        cache_key = 'character_skillplan:learned:%s' % (character.id)
        learned = cache.get(cache_key)
        # Not cached, fetch from database and cache
        if learned is None:
            learned = {}
            for cs in CharacterSkill.objects.filter(character=character).select_related('skill__item'):
                learned[cs.skill.item.id] = cs
            cache.set(cache_key, learned, 300)
    
        tt.add_time('char skills')
    
        # Possibly get training information
        training_skill = None
        if character.config.show_skill_queue is True:
            sqs = list(SkillQueue.objects.select_related('skill__item').filter(character=character, end_time__gte=utcnow))
            if sqs:
                training_skill = sqs[0]
    
        tt.add_time('training')
        
    # Initialise stat stuff
    if character and character.details:
        remap_stats = dict(
            int_attribute=character.details.int_attribute,
            mem_attribute=character.details.mem_attribute,
            per_attribute=character.details.per_attribute,
            wil_attribute=character.details.wil_attribute,
            cha_attribute=character.details.cha_attribute,
        )
        
    else:
        # default stats on a new char
        # no char will ever have 0 to any attribute
        remap_stats = dict(
            int_attribute=20,
            mem_attribute=20,
            per_attribute=20,
            wil_attribute=20,
            cha_attribute=19,
        )

    implant_stats = {}
    for stat in ('int', 'mem', 'per', 'wil', 'cha'):
        k = '%s_bonus' % (stat)
        if implants == 0 and character:
            implant_stats[k] = getattr(character.details, k, 0)
        else:
            implant_stats[k] = implants

    # Iterate over all entries in this skill plan
    entries = []
    total_remaining = 0.0
    for entry in skillplan.entries.select_related('sp_remap', 'sp_skill__skill__item__item_group'):
        # It's a remap entry
        if entry.sp_remap is not None:
        
            # If the remap have every attributes set to 0, we do not add it.
            # (happen when remap are not set on evemon before exporting .emp
            if entry.sp_remap.int_stat == 0 and entry.sp_remap.mem_stat == 0 and entry.sp_remap.per_stat == 0 and entry.sp_remap.wil_stat == 0 and entry.sp_remap.cha_stat == 0:
               continue
                
            
            # Delete the previous remap if it's two in a row, that makes no sense
            if entries and entries[-1].sp_remap is not None:
                entries.pop()


            remap_stats['int_attribute'] = entry.sp_remap.int_stat
            remap_stats['mem_attribute'] = entry.sp_remap.mem_stat
            remap_stats['per_attribute'] = entry.sp_remap.per_stat
            remap_stats['wil_attribute'] = entry.sp_remap.wil_stat
            remap_stats['cha_attribute'] = entry.sp_remap.cha_stat

        # It's a skill entry
        if entry.sp_skill is not None:
            skill = entry.sp_skill.skill
            
            # If this skill is already learned
            cs = learned.get(skill.item.id, None)
            if cs is not None:
                # Mark it as injected if level 0
                if cs.level == 0:
                    entry.z_injected = True
                # It might already be trained
                elif cs.level >= entry.sp_skill.level:
                    # If we don't care about trained skills, skip this skill entirely
                    if not show_trained:
                        continue

                    entry.z_trained = True
            # Not learned, need to buy it
            else:
                entry.z_buy = True

            # Calculate SP/hr
            if remap_stats:
                entry.z_sppm = skill.get_sppm_stats(remap_stats, implant_stats)
            else:
                entry.z_sppm = skill.get_sp_per_minute(character)
            
            # 0 sppm is bad
            entry.z_sppm = max(1, entry.z_sppm)
            entry.z_spph = int(entry.z_sppm * 60)

            # Calculate time remaining
            if training_skill is not None and training_skill.skill_id == entry.sp_skill.skill_id and training_skill.to_level == entry.sp_skill.level:
                entry.z_remaining = total_seconds(training_skill.end_time - utcnow)
                entry.z_training = True
            else:
                entry.z_remaining = (skill.get_sp_at_level(entry.sp_skill.level) - skill.get_sp_at_level(entry.sp_skill.level - 1)) / entry.z_sppm * 60

            # Add time remaining to total
            if not hasattr(entry, 'z_trained'):
                total_remaining += entry.z_remaining

        entries.append(entry)

    tt.add_time('skillplan loop')
    if settings.DEBUG:
        tt.finished()

    return {
            'show_trained': show_trained,
            'implants': implants,
            'char': character,
            'entries': entries,
            'total_remaining': total_remaining,
        }


def _handle_skillplan_upload(request):
    name = request.POST['name'].strip()
    uf = request.FILES['file']
    visibility = request.POST['visibility']

    # Check that this name is unique for the user
    if SkillPlan.objects.filter(user=request.user, name=name).count() > 0:
        request.session['message_type'] = 'error'
        request.session['message'] = "You already have a skill plan with that name!"
        return

    # Check file size, 10KB should be more than large enough
    if uf.size > 10240:
        request.session['message_type'] = 'error'
        request.session['message'] = "That file is too large!"
        return

    data = StringIO(uf.read())

    # Try opening it as a gzip file
    gf = gzip.GzipFile(fileobj=data)
    try:
        data = gf.read()
    except IOError:
        request.session['message_type'] = 'error'
        request.session['message'] = "That doesn't look like a .EMP file!"
        return

    # Make sure it's valid XML
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        request.session['message_type'] = 'error'
        request.session['message'] = "That doesn't look like a .EMP file!"
        return

    # FINALLY
    skillplan = SkillPlan.objects.create(
        user=request.user,
        name=name,
        visibility=visibility,
    )
    
    _parse_emp_plan(skillplan, root)

    request.session['message_type'] = 'success'
    request.session['message'] = "Skill plan uploaded successfully."


def _parse_emp_plan(skillplan, root):
    entries = []
    position = 0
    for entry in root.findall('entry'):
        # Create the various objects for the remapping if it exists
        remapping = entry.find('remapping')
        if remapping is not None:
            # <remapping status="UpToDate" per="17" int="27" mem="21" wil="17" cha="17" description="" />
            spr = SPRemap.objects.create(
                int_stat=remapping.attrib['int'],
                mem_stat=remapping.attrib['mem'],
                per_stat=remapping.attrib['per'],
                wil_stat=remapping.attrib['wil'],
                cha_stat=remapping.attrib['cha'],
            )

            entries.append(SPEntry(
                skill_plan=skillplan,
                position=position,
                sp_remap=spr,
            ))

            position += 1

        # Create the various objects for the skill
        try:
            sps = SPSkill.objects.create(
                skill_id=entry.attrib['skillID'],
                level=entry.attrib['level'],
                priority=entry.attrib['priority'],
            )
        except:
            continue
            
        entries.append(SPEntry(
            skill_plan=skillplan,
            position=position,
            sp_skill=sps,
        ))

        position += 1

    SPEntry.objects.bulk_create(entries)
