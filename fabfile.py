""" Fabric script to handle common iOS building tasks """
from fabric.api import local, lcd, abort, cd, run

import os

def resign_for_distribution(ipa, dist_profile, adhoc_profile, sign_name):
    local('unzip "%s.ipa"' % ipa)
    app_name = os.listdir('Payload')[0]

    def sign_with_profile(p, n):
        local('rm -rf "Payload/%s/_CodeSignature" '\
              '"Payload/%s/CodeResources"' % (app_name, app_name))
        local('cp "%s" "Payload/%s/embedded.mobileprovision"' % (p, app_name))
        local('/usr/bin/codesign -f -s "%s" '
              '--resource-rules "Payload/%s/ResourceRules.plist" '
              '"Payload/%s"' % (sign_name, app_name, app_name))
        local('zip -qr "%s.%s.ipa" Payload' % (ipa,n))

    sign_with_profile(dist_profile, 'dist')
    sign_with_profile(adhoc_profile, 'adhoc')

    local('rm -rf Payload')

def stamp_version(version, jenkins=None):
    """ Write out a version number and jenkins build

        Write out to plist that Xcode build tools will compile into
        the app """
    t_vars = {'version': version, 'build': jenkins}

    content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>version</key>
        <string>%(version)s</string>
    <key>build</key>
        <string>%(build)s</string>
</dict>
</plist>""" % t_vars

    template_file = open('./OpenTreeMap/version.plist', 'w')
    template_file.write(content)
    template_file.flush()

def create_info_plist(app_name, app_id):
    infoplist = open('OpenTreeMap/OpenTreeMap-Info.plist.template').read()
    infoplist = infoplist % { "app_name": app_name, "app_id": app_id }
    
    f = open('OpenTreeMap/OpenTreeMap-Info.plist', 'w')
    f.write(infoplist)
    f.flush()
    f.close()

def convert_choices(choices_py,choices_plist):
    globs = {}
    execfile(choices_py, globs)
    choices = globs['CHOICES']

    hippie_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>"""

    for (ch, vals) in choices.iteritems():
        hippie_xml += """
        <key>%s</key>
	<array>\n""" % ch

        for (value, txt) in vals:
            hippie_xml += """
		<dict>
			<key>key</key>
			<string>%s</string>
			<key>type</key>
			<string>int</string>
			<key>value</key>
			<string>%s</string>
		</dict>\n""" % (value,txt)

        hippie_xml += "        </array>\n"

    hippie_xml += "</dict>\n"
    hippie_xml += "</plist>"

    f = open(choices_plist, 'w')
    f.write(hippie_xml)
    f.flush()
    f.close()



def clone_skin_repo(skin=None, clone_dir=None, version=None, user=None):
    """ Clone a skin repo

    Require arguments:
    skin - Name of the skin to download (Greenprint, Philadelphia, etc)
    version - Skin version to download (v1.1, git commit hash, etc)

    Note, you can specify the skin and the version together:
    clone_skin_repo(skin='Philadelphia@v1.2')

    Optional Arguments:
    clone_dir - Directory to clone to. If empty the clone will go into
                the current directory
    user - Specify a user to download via ssh, otherwise download
           public git

    """
    if skin and "@" in skin:
        if version:
            abort("Specify version via @ or version but not both")

        (skin, version) = skin.split("@")

    if not version:
        print "[Warn] Version not specified. Using 'master'"
        version = 'master'

    if user:  # If user is specified we are cloning an Azavea internal repository
        git_remote_path = 'ssh://%s@git.internal.azavea.com'\
                          '/git/Azavea_OpenTreeMap/%s.git'\
                          % (user, skin)
    elif skin:  # If skin is specified we are cloning an Azavea internal repository
        git_remote_path = 'git://git.internal.azavea.com/'\
                          'git/Azavea_OpenTreeMap/%s.git'\
                          % skin
    else:
        git_remote_path = 'https://github.com/azavea/OpenTreeMap-iOS-skin.git'

    if clone_dir and skin:
        git_local_path = '%s/%s' % (clone_dir, skin)
    elif clone_dir:
        git_local_path = '%s/%s' % (clone_dir, 'MobileSkin')
    else:
        git_local_path = 'MobileSkin'

    local('git clone -b %s "%s" "%s"' %
          (version, git_remote_path, git_local_path))


def install_skin(skin=None, user=None, version=None, clone_dir=None, 
                 force_delete=None):
    """ Install the given skin

    Optionally specify clone_dir to control where the repository
    will be cloned to. Default is one level above this one

    If the repository has already been checked out (i.e.
    <clone_dir>/<skin>/ios exists) then you only need to
    run this command with the 'skin' argument.

    For details about the other arguments checkout `clone_skin_repo`

    Set 'force_delete' to True to delete any previous repos
    """
    if not clone_dir:
        clone_dir = '..'

    if skin:
        git_clone_path = '%s/%s' % (clone_dir, skin)
    else:
        git_clone_path = '%s/MobileSkin' % clone_dir

    if force_delete:
        local('rm -rf "%s"' % git_clone_path)

    if not os.path.exists('%s/ios' % git_clone_path):
        clone_skin_repo(skin, clone_dir, version, user)

    with lcd('OpenTreeMap'):
        local('rm -f skin')
        local('ln -s "../%s/ios" skin' % git_clone_path)

    with lcd('OpenTreeMap'):
        local('rm -f "Default.png" "Default@2x.png" '\
              '"Icon.png" "Icon@2x.png" "Icon-72.png" "Icon-72@2x.png"')
        local('cp "../%s/ios/images/splash_screen.png" '\
              'Default.png' % git_clone_path)
        local('cp "../%s/ios/images/splash_screen@2x.png" '\
              '"Default@2x.png"' % git_clone_path)
        local('cp "../%s/ios/icons/iphone_app-icon.png" '\
              'Icon.png' % git_clone_path)
        local('cp "../%s/ios/icons/iphone_app-icon@2x.png" '\
              '"Icon@2x.png"' % git_clone_path)
        local('cp "../%s/ios/icons/ipad_app-icon.png" '\
              'Icon-72.png' % git_clone_path)
        local('cp "../%s/ios/icons/ipad_app-icon@2x.png" '\
              'Icon-72@2x.png' % git_clone_path)

    convert_choices("%s/choices.py" % git_clone_path, "OpenTreeMap/Choices.plist")
        
