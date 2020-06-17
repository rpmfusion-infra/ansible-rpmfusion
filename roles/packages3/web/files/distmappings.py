# Global list of koji tags we care about
tags = ({'name': 'Rawhide Free', 'tag': 'f33-free'},
        {'name': 'Rawhide NonFree', 'tag': 'f33-nonfree'},

        {'name': 'Fedora 32 Free', 'tag': 'f32-free-updates'},
        {'name': 'Fedora 32 Free', 'tag': 'f32-free'},
        {'name': 'Fedora 32 Free Testing', 'tag': 'f32-free-updates-testing'},

        {'name': 'Fedora 32 NonFree', 'tag': 'f32-nonfree-updates'},
        {'name': 'Fedora 32 NonFree', 'tag': 'f32-nonfree'},
        {'name': 'Fedora 32 NonFree Testing', 'tag': 'f32-nonfree-updates-testing'},

        {'name': 'Fedora 31 Free', 'tag': 'f31-free-updates'},
        {'name': 'Fedora 31 Free', 'tag': 'f31-free'},
        {'name': 'Fedora 31 Free Testing', 'tag': 'f31-free-updates-testing'},

        {'name': 'Fedora 31 NonFree', 'tag': 'f31-nonfree-updates'},
        {'name': 'Fedora 31 NonFree', 'tag': 'f31-nonfree'},
        {'name': 'Fedora 31 NonFree Testing', 'tag': 'f31-nonfree-updates-testing'},


        {'name': 'EPEL 8 Free', 'tag': 'el8-free'},
        {'name': 'EPEL 8 Free Testing', 'tag': 'el8-free-testing'},
        {'name': 'EPEL 8 NonFree', 'tag': 'el8-nonfree'},
        {'name': 'EPEL 8 NonFree Testing', 'tag': 'el8-nonfree-testing'},

        {'name': 'EPEL 7 Free', 'tag': 'el7-free'},
        {'name': 'EPEL 7 Free Testing', 'tag': 'el7-free-testing'},
        {'name': 'EPEL 7 NonFree', 'tag': 'el7-nonfree'},
        {'name': 'EPEL 7 NonFree Testing', 'tag': 'el7-nonfree-testing'},

        {'name': 'EPEL 6 Free', 'tag': 'el6-free'},
        {'name': 'EPEL 6 Free Testing', 'tag': 'el6-free-testing'},
        {'name': 'EPEL 6 NonFree', 'tag': 'el6-nonfree'},
        {'name': 'EPEL 6 NonFree Testing', 'tag': 'el6-nonfree-testing'},

       )

tags_to_name_map = {}
for t in tags:
    tags_to_name_map[t['tag']] = t['name']
