import os, shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.hashcompat import sha_constructor
from django.db import transaction

from massmedia import settings as appsettings
from massmedia.models import Image, is_image

from optparse import make_option

try:
    import paramiko as ftpclient
except ImportError:
    ftpclient = None

try:
    import Image as PilImage
except ImportError:
    try:
        from PIL import Image as PilImage
    except ImportError:
        PilImage = 0


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-t', '--type', dest='type', default='1',
            help='Indicates type of connection, only local and ftp atm.'
        ),
        make_option('-u', '--user', dest='user', default='1',
            help='Indicates user for ftp.'
        ),
        make_option('-p', '--pwd', dest='pwd', default='1',
            help='Indicates password for ftp.'
        ),
        make_option('-i', '--host', dest='ip', default='1',
            help='Indicates host for ftp.'
        ),
        make_option('-d', '--dir', dest='path', default='1',
            help='Indicates path for ftp.'
        ),
    )
    @transaction.commit_manually
    def handle(self, *args, **options):
        print 'Import started...'
        if not 'path' in options:
            return
        path = options['path']
        archived_path = os.path.join(path, 'archive')
        if not os.path.exists(archived_path):
            os.mkdir(archived_path)
        
        if 'type' in options and options['type'] == 'ftp' and ftpclient:
            print 'Using remote options..'
            if 'ip' in options:
                host = options['ip']
            if 'user' in options:
                user = options['user']
            if 'pwd' in options:
                pwd = options['pwd']
            try:
                transport = ftpclient.Transport(host)
                transport.connect(username=user, password=pwd)
                ftp = ftpclient.SFTPClient.from_transport(transport)
                
                images = filter(is_image, ftp.listdir(path))
                local = appsettings.IMPORT_LOCAL_TMP_DIR + '%s'
                remote = path + '%s'
                for fi in images:
                    print 'Getting image: %s' % fi
                    try:
                        ftp.get(remote % fi, local % fi)
                    except Exception, e:
                        print 'Get Image Failed: %s' % e
                        continue
                        
                local_images = [os.path.join(appsettings.IMPORT_LOCAL_TMP_DIR, x) for x in os.listdir(appsettings.IMPORT_LOCAL_TMP_DIR) if is_image(x)]
                for image in local_images:
                    print 'Procssing image: %s' % image
                    try:
                        img = Image.objects.create(title=os.path.basename(image),slug=sha_constructor(image+str(os.stat(image).st_size)).hexdigest())
                        img.file.save(os.path.basename(image),
                            ContentFile(open(image,'rb').read()))
                        transaction.commit()
                    except Exception, e:
                        transaction.rollback()
                        print 'Caught exception: %s' % e
                        continue
                                  
                ftp.close()
                transport.close()
            except Exception, e:
                transaction.rollback()
                print 'Caught exception: %s' % e
                try:
                    ftp.close()
                except:
                    pass
                try:
                    transport.close()
                except:
                    pass
        else:
            print 'Using local options...'
            images = [os.path.join(path, x) for x in os.listdir(path) if is_image(x)]
        
            for image in images:
                print 'Processing image: %s' % image
                try:
                    try:
                        im = PilImage.open(open(image,'rb'))
                        im.verify()
                    except Exception, e:
                        print 'Image open exception: %s' % e
                        try:
                            print 'Tring to Move image to archive...'
                            shutil.move(image, os.path.join(archived_path, os.path.basename(image)))
                            print 'Move Complete'
                        except Exception, e:
                            print 'Move exception: %s' % e
                            
                        continue
                        
                    img = Image.objects.create(title=os.path.basename(image),slug=sha_constructor(image+str(os.stat(image).st_size)).hexdigest())
                    img.file.save(os.path.basename(image),
                        ContentFile(open(image,'rb').read()))
                    transaction.commit()
                    
                    # Archive processed file
                    try:
                        print 'Tring to Move image to archive...'
                        shutil.move(image, os.path.join(archived_path, os.path.basename(image)))
                        print 'Move Complete'
                    except Exception, e:
                        print 'Move exception: %s' % e
                    
                    if isinstance(img.metadata, list) and len(img.metadata) > 0:
                        if 120 in img.metadata[0].keys():
                            img.caption = img.metadata[0][120]
                            img.save()
                            transaction.commit()
                        
                except Exception, e:
                    transaction.rollback()
                    print 'Caught exception: %s' % e
                    try:
                        print 'Tring to Move image to archive...'
                        shutil.move(image, os.path.join(archived_path, os.path.basename(image)))
                        print 'Move Complete'
                    except Exception, e:
                        print 'Move exception: %s' % e
                    continue
        
        print 'Image import complete.'    