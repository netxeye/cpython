import mkcwproject
import sys
import os
import string

PYTHONDIR = sys.prefix
PROJECTDIR = os.path.join(PYTHONDIR, ":Mac:Build")
MODULEDIRS = [	# Relative to projectdirs
	"::Modules:%s",
	"::Modules",
	":::Modules",
]

# Global variable to control forced rebuild (otherwise the project is only rebuilt
# when it is changed)
FORCEREBUILD=0

def relpath(base, path):
	"""Turn abs path into path relative to another. Only works for 2 abs paths
	both pointing to folders"""
	if not os.path.isabs(base) or not os.path.isabs(path):
		raise 'Absolute paths only'
	if base[-1] == ':':
		base = base[:-1]
	basefields = string.split(base, os.sep)
	pathfields = string.split(path, os.sep)
	commonfields = len(os.path.commonprefix((basefields, pathfields)))
	basefields = basefields[commonfields:]
	pathfields = pathfields[commonfields:]
	pathfields = ['']*(len(basefields)+1) + pathfields
	rv = string.join(pathfields, os.sep)
	return rv

def genpluginproject(architecture, module,
		project=None, projectdir=None,
		sources=[], sourcedirs=[],
		libraries=[], extradirs=[],
		extraexportsymbols=[], outputdir=":::Lib:lib-dynload",
		libraryflags=None, stdlibraryflags=None, prefixname=None,
		initialize=None):
	if architecture != "carbon":
		raise 'Unsupported architecture: %s'%architecture
	templatename = "template-%s" % architecture
	targetname = "%s.%s" % (module, architecture)
	dllname = "%s.%s.slb" % (module, architecture)
	if not project:
		project = "%s.%s.mcp"%(module, architecture)
	if not projectdir:
		projectdir = PROJECTDIR
	if not sources:
		sources = [module + 'module.c']
	if not sourcedirs:
		for moduledir in MODULEDIRS:
			if '%' in moduledir:
				# For historical reasons an initial _ in the modulename
				# is not reflected in the folder name
				if module[0] == '_':
					modulewithout_ = module[1:]
				else:
					modulewithout_ = module
				moduledir = moduledir % modulewithout_
			fn = os.path.join(projectdir, os.path.join(moduledir, sources[0]))
			if os.path.exists(fn):
				moduledir, sourcefile = os.path.split(fn)
				sourcedirs = [relpath(projectdir, moduledir)]
				sources[0] = sourcefile
				break
		else:
			print "Warning: %s: sourcefile not found: %s"%(module, sources[0])
			sourcedirs = []
	if prefixname:
		pass
	elif architecture == "carbon":
		prefixname = "mwerks_shcarbon_pch"
	else:
		prefixname = "mwerks_plugin_config.h"
	dict = {
		"sysprefix" : relpath(projectdir, sys.prefix),
		"sources" : sources,
		"extrasearchdirs" : sourcedirs + extradirs,
		"libraries": libraries,
		"mac_outputdir" : outputdir,
		"extraexportsymbols" : extraexportsymbols,
		"mac_targetname" : targetname,
		"mac_dllname" : dllname,
		"prefixname" : prefixname,
	}
	if libraryflags:
		dict['libraryflags'] = libraryflags
	if stdlibraryflags:
		dict['stdlibraryflags'] = stdlibraryflags
	if initialize:
		dict['initialize'] = initialize
	mkcwproject.mkproject(os.path.join(projectdir, project), module, dict, 
			force=FORCEREBUILD, templatename=templatename)

def	genallprojects(force=0):
	global FORCEREBUILD
	FORCEREBUILD = force
	# Standard Python modules
	genpluginproject("carbon", "pyexpat", 
		sources=["pyexpat.c", "xmlparse.c", "xmlrole.c", "xmltok.c"],
		extradirs=[":::Modules:expat"],
		prefixname="mwerks_shcarbon_config.h"
		)
	genpluginproject("carbon", "zlib", 
		libraries=["zlib.ppc.Lib"], 
		extradirs=["::::imglibs:zlib:mac", "::::imglibs:zlib"])
	genpluginproject("carbon", "gdbm", 
		libraries=["gdbm.ppc.gusi.lib"], 
		extradirs=["::::gdbm:mac", "::::gdbm"])
	genpluginproject("carbon", "_weakref", sources=["_weakref.c"])
	genpluginproject("carbon", "_symtable", sources=["symtablemodule.c"])
	# Example/test modules
	genpluginproject("carbon", "_testcapi")
	genpluginproject("carbon", "xx")
	genpluginproject("carbon", "xxsubtype", sources=["xxsubtype.c"])
	genpluginproject("carbon", "_hotshot", sources=["_hotshot.c"])
	
	# bgen-generated Toolbox modules
	genpluginproject("carbon", "_AE", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_AH", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_App", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Cm", outputdir="::Lib:Carbon")
	# XXX can't work properly because we need to set a custom fragment initializer
	#genpluginproject("carbon", "_CG", 
	#		sources=["_CGModule.c", "CFMLateImport.c"],
	#		libraries=["CGStubLib"],
	#		outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Ctl", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Dlg", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Drag", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Evt", 
			stdlibraryflags="Debug, WeakImport",  outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_File", 
			stdlibraryflags="Debug, WeakImport",  outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Fm", 
			stdlibraryflags="Debug, WeakImport",  outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Folder", 
			stdlibraryflags="Debug, WeakImport",  outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Help", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_IBCarbon", sources=[":ibcarbon:_IBCarbon.c"], 
			outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Icn", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_List", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Menu", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Qd", 
			stdlibraryflags="Debug, WeakImport",  outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Qt", 
			libraryflags="Debug, WeakImport",  outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Qdoffs", 
			stdlibraryflags="Debug, WeakImport",  outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Res", 
			stdlibraryflags="Debug, WeakImport", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Scrap", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Snd", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Sndihooks", sources=[":snd:_Sndihooks.c"], outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_TE", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Mlte", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_Win", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_CF", sources=["_CFmodule.c", "pycfbridge.c"], outputdir="::Lib:Carbon")
	genpluginproject("carbon", "_CarbonEvt", outputdir="::Lib:Carbon")
	genpluginproject("carbon", "hfsplus")
	
	# Other Mac modules
	genpluginproject("carbon", "calldll", sources=["calldll.c"])
	genpluginproject("carbon", "ColorPicker")
	genpluginproject("carbon", "waste",
		sources=[
			"wastemodule.c",
			"WEObjectHandlers.c",
			"WETabs.c", "WETabHooks.c"],
		libraries=["WASTE.Carbon.lib"],
		extradirs=[
			'{Compiler}:MacOS Support:(Third Party Support):Waste 2.0 Distribution:C_C++ Headers',
			'{Compiler}:MacOS Support:(Third Party Support):Waste 2.0 Distribution:Static Libraries',
			'::wastemods',
			]
		)
	genpluginproject("carbon", "icglue", sources=["icgluemodule.c"])

if __name__ == '__main__':
	genallprojects()
	
	
