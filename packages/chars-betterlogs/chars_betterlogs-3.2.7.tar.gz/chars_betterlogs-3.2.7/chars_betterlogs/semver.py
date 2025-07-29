from __future__ import annotations

class SemVer:
    r'''Modified version of the Semantic Versioning system that allows for an additional string identifier.
    
    E.G: `1.3.2h`'''
    
    major:int; minor:int; patch:int; identifier:(str | None)

    def __init__(self, major:int= 0, minor:int = 1, patch:int = 0, identifier:(str |  None) = None) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.identifier = identifier

    def __str__(self):
        return self.toString()
    
    def __repr__(self):
        fString = f'{self.major}, {self.minor}, {self.patch}'
        if self.identifier != None: fString += ', ' + f"'{self.identifier}'"

        return f'SemVer({fString})'

    def toString(self, places:int = 3)->str:
        r'''Returns the full version string as `major.minor.patch<Identifier>`
        
        `places : int` | How far to include the version string | 1+ = major, 2+ = major.minor 3+ = major.minor.patch'''
        ver = ''
        if places >= 1: ver += str(self.major)
        if places >= 2: ver += f'.{str(self.minor)}'
        if places >= 3: ver += f'.{str(self.patch)}'
        if self.identifier != None: ver += self.identifier

        return ver
    
    def fromString(s:str) -> SemVer:
        verArray = s.split('.')
        
        ver = SemVer(0, 0, 0)
        if verArray.__len__() >= 1: ver.major = int(verArray[0])
        if verArray.__len__() >= 2: ver.minor = int(verArray[1])
        if verArray.__len__() == 3:
            try: ver.patch = int(verArray[2])
            except: 
                patchStringSplit = verArray[2].split()

                ver.patch = int(patchStringSplit[0])
                patchStringSplit.pop(0)

                newVersion = ''
                for char in patchStringSplit:
                    newVersion+=char
                ver.identifier = newVersion
    
    def greaterThan(self, version:SemVer) -> bool:
        r'Checks if another SemVer is greater than this SemVer (Ignores Identifier.)'
        if self.major > version.major: return True
        if self.major == version.major and self.minor > version.minor: return True
        if self.major== version.major and self.minor == version.minor and self.patch > version.patch: return True
        return False
    
    def greaterThanOrEqual(self, version:SemVer) -> bool:
        r'Checks if another SemVer is greater than or equal to this SemVer (Ignores Identifier.)'
        if (self.greaterThan(version)): return True
        if self.major== version.major and self.minor == version.minor and self.patch == version.patch: return True
        return False

    def lessThan(self, version:SemVer) -> bool:
        r'Checks if another SemVer is less than this SemVer (Ignores Identifier.)'
        if self.major < version.major: return True
        if self.major == version.major and self.minor < version.minor: return True
        if self.major== version.major and self.minor == version.minor and self.patch < version.patch: return True
        return False
    
    def lessThanOrEqual(self, version:SemVer)->bool:
        r'Checks if another SemVer is less than or equal to this SemVer (Ignores Identifier.)'
        if (self.lessThan(version)): return True
        if self.major == version.major and self.minor == version.minor and self.patch == version.patch: return True
        return False