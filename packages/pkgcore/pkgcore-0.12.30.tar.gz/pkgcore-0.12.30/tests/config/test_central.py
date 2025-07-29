import pytest
from snakeoil.errors import walk_exception_chain

from pkgcore.config import basics, central, errors
from pkgcore.config.hint import configurable


# A bunch of functions used from various tests below.
def repo(cache):
    return cache


@configurable(types={"content": "ref:drawer", "contents": "refs:drawer"})
def drawer(content=None, contents=None):
    return content, contents


# The exception checks here also check if the str value of the
# exception is what we expect. This does not mean the wording of the
# error messages used here is strictly required. It just makes sure
# the error we get is the expected one and is useful. Please make sure
# you check for a sensible error message when more tests are added.

# A lot of the ConfigManager instances get object() as a remote type.
# This makes sure the types are not unnecessarily queried (since
# querying object() will blow up).


class RemoteSource:
    """Use this one for tests that do need the names but nothing more."""

    def __iter__(self):
        return iter(("remote",))

    def __getitem__(self, key):
        raise NotImplementedError()


def _str_exc(exc):
    return ":\n".join(str(x) for x in walk_exception_chain(exc))


def check_error(message, func, *args, **kwargs):
    """Like assertRaises but checks for the message string too."""
    klass = kwargs.pop("klass", errors.ConfigurationError)
    try:
        func(*args, **kwargs)
    except klass as exc:
        assert message == _str_exc(exc), (
            f"\nGot:\n{_str_exc(exc)!r}\nExpected:\n{message!r}\n"
        )
    else:
        pytest.fail("no exception raised")


def get_config_obj(manager, obj_type, obj_name):
    types = getattr(manager.objects, obj_type)
    return types[obj_name]


def test_sections():
    manager = central.ConfigManager(
        [
            {
                "fooinst": basics.HardCodedConfigSection({"class": repo}),
                "barinst": basics.HardCodedConfigSection({"class": drawer}),
            }
        ]
    )
    assert ["barinst", "fooinst"] == sorted(manager.sections())
    assert list(manager.objects.drawer.keys()) == ["barinst"]
    assert manager.objects.drawer == {"barinst": (None, None)}


def test_contains():
    manager = central.ConfigManager(
        [{"spork": basics.HardCodedConfigSection({"class": drawer})}], [RemoteSource()]
    )
    assert "spork" in manager.objects.drawer
    assert "foon" not in manager.objects.drawer


def test_no_class():
    manager = central.ConfigManager([{"foo": basics.HardCodedConfigSection({})}])
    check_error(
        "Collapsing section named 'foo':\nno class specified",
        manager.collapse_named_section,
        "foo",
    )


def test_missing_section_ref():
    manager = central.ConfigManager(
        [
            {
                "rsync repo": basics.HardCodedConfigSection({"class": repo}),
            }
        ]
    )
    check_error(
        "Collapsing section named 'rsync repo':\n"
        "type tests.config.test_central.repo needs settings for "
        "'cache'",
        get_config_obj,
        manager,
        "repo",
        "rsync repo",
    )


def test_unknown_type():
    manager = central.ConfigManager(
        [{"spork": basics.HardCodedConfigSection({"class": drawer, "foon": None})}]
    )
    check_error(
        "Collapsing section named 'spork':\nType of 'foon' unknown",
        manager.collapse_named_section,
        "spork",
    )


def test_missing_inherit_target():
    manager = central.ConfigManager(
        [
            {
                "myrepo": basics.HardCodedConfigSection(
                    {
                        "class": repo,
                        "inherit": ["baserepo"],
                    }
                ),
            }
        ],
        [RemoteSource()],
    )
    check_error(
        "Collapsing section named 'myrepo':\nInherit target 'baserepo' cannot be found",
        get_config_obj,
        manager,
        "repo",
        "myrepo",
    )


def test_inherit_unknown_type():
    manager = central.ConfigManager(
        [
            {
                "baserepo": basics.HardCodedConfigSection(
                    {
                        "cache": "available",
                    }
                ),
                "actual repo": basics.HardCodedConfigSection(
                    {
                        "class": drawer,
                        "inherit": ["baserepo"],
                    }
                ),
            }
        ]
    )
    check_error(
        "Collapsing section named 'actual repo':\nType of 'cache' unknown",
        get_config_obj,
        manager,
        "repo",
        "actual repo",
    )


def test_inherit():
    manager = central.ConfigManager(
        [
            {
                "baserepo": basics.HardCodedConfigSection(
                    {
                        "cache": "available",
                        "inherit": ["unneeded"],
                    }
                ),
                "unneeded": basics.HardCodedConfigSection({"cache": "unavailable"}),
                "actual repo": basics.HardCodedConfigSection(
                    {
                        "class": repo,
                        "inherit": ["baserepo"],
                    }
                ),
            }
        ]
    )

    assert "available" == manager.objects.repo["actual repo"]


def test_no_object_returned():
    def noop():
        """Do not do anything."""

    manager = central.ConfigManager(
        [
            {
                "myrepo": basics.HardCodedConfigSection({"class": noop}),
            }
        ]
    )
    check_error(
        "Failed instantiating section 'myrepo':\n"
        "'No object returned' instantiating "
        "tests.config.test_central.noop",
        manager.collapse_named_section("myrepo").instantiate,
    )


def test_not_callable():
    class myrepo:
        def __repr__(self):
            return "useless"

    manager = central.ConfigManager(
        [
            {
                "myrepo": basics.HardCodedConfigSection({"class": myrepo()}),
            }
        ]
    )
    check_error(
        "Collapsing section named 'myrepo':\n"
        "Failed converting argument 'class' to callable:\n"
        "useless is not callable",
        get_config_obj,
        manager,
        "myrepo",
        "myrepo",
    )


def test_raises_instantiationerror():
    def myrepo():
        raise Exception("I raised")

    manager = central.ConfigManager(
        [
            {
                "myrepo": basics.HardCodedConfigSection({"class": myrepo}),
            }
        ]
    )
    check_error(
        "Failed instantiating section 'myrepo':\n"
        "Failed instantiating section 'myrepo': exception caught from 'tests.config.test_central.myrepo':\n"
        "I raised",
        get_config_obj,
        manager,
        "myrepo",
        "myrepo",
    )


def test_raises():
    def myrepo():
        raise ValueError("I raised")

    manager = central.ConfigManager(
        [{"myrepo": basics.HardCodedConfigSection({"class": myrepo})}]
    )
    check_error(
        "Failed instantiating section 'myrepo':\n"
        "Failed instantiating section 'myrepo': exception caught from 'tests.config.test_central.myrepo':\n"
        "I raised",
        get_config_obj,
        manager,
        "myrepo",
        "myrepo",
    )
    manager = central.ConfigManager(
        [{"myrepo": basics.HardCodedConfigSection({"class": myrepo})}], debug=True
    )
    check_error(
        "Failed instantiating section 'myrepo':\n"
        "Failed instantiating section 'myrepo': exception caught from 'tests.config.test_central.myrepo':\n"
        "I raised",
        get_config_obj,
        manager,
        "myrepo",
        "myrepo",
        klass=errors.ConfigurationError,
    )


def test_pargs():
    @configurable(types={"p": "str", "notp": "str"}, positional=["p"], required=["p"])
    def myrepo(*args, **kwargs):
        return args, kwargs

    manager = central.ConfigManager(
        [
            {
                "myrepo": basics.HardCodedConfigSection(
                    {
                        "class": myrepo,
                        "p": "pos",
                        "notp": "notpos",
                    }
                ),
            }
        ]
    )

    assert manager.objects.myrepo["myrepo"] == (("pos",), {"notp": "notpos"})


def test_autoexec():
    @configurable(typename="configsection")
    def autoloader():
        return {
            "spork": basics.HardCodedConfigSection({"class": repo, "cache": "test"})
        }

    manager = central.ConfigManager(
        [
            {
                "autoload-sub": basics.HardCodedConfigSection(
                    {
                        "class": autoloader,
                    }
                )
            }
        ]
    )
    assert {"autoload-sub", "spork"} == set(manager.sections())
    assert ["spork"] == list(manager.objects.repo.keys())
    assert "test" == manager.collapse_named_section("spork").instantiate()


def test_reload():
    mod_dict = {"class": repo, "cache": "test"}

    @configurable(typename="configsection")
    def autoloader():
        return {"spork": basics.HardCodedConfigSection(mod_dict)}

    manager = central.ConfigManager(
        [{"autoload-sub": basics.HardCodedConfigSection({"class": autoloader})}]
    )

    assert {"autoload-sub", "spork"} == set(manager.sections())
    assert ["spork"] == list(manager.objects.repo.keys())
    collapsedspork = manager.collapse_named_section("spork")
    assert "test" == collapsedspork.instantiate()
    mod_dict["cache"] = "modded"
    assert collapsedspork is manager.collapse_named_section("spork")
    assert "test" == collapsedspork.instantiate()
    types = manager.types
    manager.reload()
    newspork = manager.collapse_named_section("spork")
    assert collapsedspork is not newspork
    assert "modded" == newspork.instantiate(), (
        "it did not throw away the cached instance"
    )
    assert types is not manager.types


def test_instantiate_default_ref():
    manager = central.ConfigManager(
        [
            {
                "spork": basics.HardCodedConfigSection({"class": drawer}),
            }
        ]
    )
    assert (None, None) == manager.collapse_named_section("spork").instantiate()


def test_allow_unknowns():
    @configurable(allow_unknowns=True)
    def myrepo(**kwargs):
        return kwargs

    manager = central.ConfigManager(
        [{"spork": basics.HardCodedConfigSection({"class": myrepo, "spork": "foon"})}]
    )

    assert {"spork": "foon"} == manager.collapse_named_section("spork").instantiate()


def test_reinstantiate_after_raise():
    # The most likely bug this tests for is attempting to
    # reprocess already processed section_ref args.
    spork = object()

    @configurable(types={"thing": "ref:spork"})
    def myrepo(thing):
        assert thing is spork
        raise errors.ComplexInstantiationError("I suck")

    @configurable(typename="spork")
    def spork_producer():
        return spork

    manager = central.ConfigManager(
        [
            {
                "spork": basics.HardCodedConfigSection(
                    {
                        "class": myrepo,
                        "thing": basics.HardCodedConfigSection(
                            {
                                "class": spork_producer,
                            }
                        ),
                    }
                )
            }
        ]
    )
    spork = manager.collapse_named_section("spork")
    for i in range(3):
        check_error(
            "Failed instantiating section 'spork':\n"
            "Failed instantiating section 'spork': exception caught from 'tests.config.test_central.myrepo':\n"
            "'I suck', callable unset!",
            spork.instantiate,
        )
    for i in range(3):
        check_error(
            "Failed instantiating section 'spork':\n"
            "Failed instantiating section 'spork': exception caught from 'tests.config.test_central.myrepo':\n"
            "'I suck', callable unset!",
            manager.collapse_named_section("spork").instantiate,
        )


def test_instantiation_caching():
    @configurable(typename="drawer")
    def myrepo():
        return object()

    manager = central.ConfigManager(
        [
            {
                "spork": basics.HardCodedConfigSection({"class": myrepo}),
                "drawer": basics.ConfigSectionFromStringDict(
                    {
                        "class": "tests.config.test_central.drawer",
                        "content": "spork",
                    }
                ),
            }
        ]
    )

    config = manager.collapse_named_section("spork")
    assert config.instantiate() is config.instantiate()
    assert (
        config.instantiate()
        is manager.collapse_named_section("drawer").instantiate()[0]
    )


def test_collapse_named_errors():
    manager = central.ConfigManager(
        [
            {
                "spork": basics.ConfigSectionFromStringDict(
                    {"class": "tests.config.test_central.drawer", "content": "ref"}
                )
            }
        ],
        [RemoteSource()],
    )
    with pytest.raises(KeyError):
        get_config_obj(manager, "repo", "foon")
    check_error(
        "Collapsing section named 'spork':\n"
        "Failed collapsing section key 'content':\n"
        "no section called 'ref'",
        get_config_obj,
        manager,
        "repo",
        "spork",
    )


def test_recursive_autoload():
    @configurable(typename="configsection")
    def autoloader():
        return {
            "autoload-sub": basics.HardCodedConfigSection({"class": autoloader}),
            "spork": basics.HardCodedConfigSection({"class": repo, "cache": "test"}),
        }

    check_error(
        "New config is trying to modify existing section(s) 'autoload-sub' "
        "that was already instantiated.",
        central.ConfigManager,
        [
            {
                "autoload-sub": basics.HardCodedConfigSection(
                    {
                        "class": autoloader,
                    }
                )
            }
        ],
    )


def test_recursive_section_ref():
    manager = central.ConfigManager(
        [
            {
                "spork": basics.ConfigSectionFromStringDict(
                    {"class": "tests.config.test_central.drawer", "content": "foon"}
                ),
                "foon": basics.ConfigSectionFromStringDict(
                    {"class": "tests.config.test_central.drawer", "content": "spork"}
                ),
                "self": basics.ConfigSectionFromStringDict(
                    {"class": "tests.config.test_central.drawer", "content": "self"}
                ),
            }
        ]
    )
    check_error(
        "Collapsing section named 'self':\n"
        "Failed collapsing section key 'content':\n"
        "Reference to 'self' is recursive",
        get_config_obj,
        manager,
        "drawer",
        "self",
    )
    check_error(
        "Collapsing section named 'spork':\n"
        "Failed collapsing section key 'content':\n"
        "Collapsing section named 'foon':\n"
        "Failed collapsing section key 'content':\n"
        "Reference to 'spork' is recursive",
        get_config_obj,
        manager,
        "drawer",
        "spork",
    )


def test_recursive_inherit():
    manager = central.ConfigManager(
        [
            {
                "spork": basics.ConfigSectionFromStringDict(
                    {"class": "tests.config.test_central.drawer", "inherit": "foon"}
                ),
                "foon": basics.ConfigSectionFromStringDict(
                    {"class": "tests.config.test_central.drawer", "inherit": "spork"}
                ),
            }
        ]
    )
    check_error(
        "Collapsing section named 'spork':\nInherit 'spork' is recursive",
        get_config_obj,
        manager,
        "drawer",
        "spork",
    )


def test_alias():
    def myspork():
        return object

    manager = central.ConfigManager(
        [
            {
                "spork": basics.HardCodedConfigSection({"class": myspork}),
                "foon": basics.section_alias("spork", "myspork"),
            }
        ]
    )
    # This tests both the detected typename of foon and the caching.
    assert manager.objects.myspork["spork"] is manager.objects.myspork["foon"]


def test_typecheck():
    @configurable(types={"myrepo": "ref:repo"}, typename="repo")
    def reporef(myrepo=None):
        return myrepo

    @configurable(types={"myrepo": "refs:repo"}, typename="repo")
    def reporefs(myrepo=None):
        return myrepo

    @configurable(typename="repo")
    def myrepo():
        return "repo!"

    manager = central.ConfigManager(
        [
            {
                "myrepo": basics.HardCodedConfigSection({"class": myrepo}),
                "drawer": basics.HardCodedConfigSection({"class": drawer}),
                "right": basics.AutoConfigSection(
                    {"class": reporef, "myrepo": "myrepo"}
                ),
                "wrong": basics.AutoConfigSection(
                    {"class": reporef, "myrepo": "drawer"}
                ),
            }
        ]
    )
    check_error(
        "Collapsing section named 'wrong':\n"
        "Failed collapsing section key 'myrepo':\n"
        "reference 'drawer' should be of type 'repo', got 'drawer'",
        get_config_obj,
        manager,
        "repo",
        "wrong",
    )
    assert "repo!" == manager.objects.repo["right"]

    manager = central.ConfigManager(
        [
            {
                "myrepo": basics.HardCodedConfigSection({"class": myrepo}),
                "drawer": basics.HardCodedConfigSection({"class": drawer}),
                "right": basics.AutoConfigSection(
                    {"class": reporefs, "myrepo": "myrepo"}
                ),
                "wrong": basics.AutoConfigSection(
                    {"class": reporefs, "myrepo": "drawer"}
                ),
            }
        ]
    )
    check_error(
        "Collapsing section named 'wrong':\n"
        "Failed collapsing section key 'myrepo':\n"
        "reference 'drawer' should be of type 'repo', got 'drawer'",
        get_config_obj,
        manager,
        "repo",
        "wrong",
    )
    assert ["repo!"] == manager.objects.repo["right"]


def test_default():
    manager = central.ConfigManager(
        [
            {
                "thing": basics.HardCodedConfigSection(
                    {"class": drawer, "default": True}
                ),
                "bug": basics.HardCodedConfigSection(
                    {"class": None, "inherit-only": True, "default": True}
                ),
                "ignore": basics.HardCodedConfigSection({"class": drawer}),
            }
        ]
    )
    assert (None, None) == manager.get_default("drawer")
    assert manager.collapse_named_section("thing").default

    manager = central.ConfigManager(
        [
            {
                "thing": basics.HardCodedConfigSection(
                    {"class": drawer, "default": True}
                ),
                "thing2": basics.HardCodedConfigSection(
                    {"class": drawer, "default": True}
                ),
            }
        ]
    )
    check_error(
        "type drawer incorrectly has multiple default sections: 'thing', 'thing2'",
        manager.get_default,
        "drawer",
    )

    manager = central.ConfigManager([])
    assert manager.get_default("drawer") is None


def test_broken_default():
    def broken():
        raise errors.ComplexInstantiationError("broken")

    manager = central.ConfigManager(
        [
            {
                "thing": basics.HardCodedConfigSection(
                    {
                        "class": drawer,
                        "default": True,
                        "content": basics.HardCodedConfigSection({"class": "spork"}),
                    }
                ),
                "thing2": basics.HardCodedConfigSection(
                    {"class": broken, "default": True}
                ),
            }
        ]
    )
    check_error(
        "Collapsing defaults for 'drawer':\n"
        "Collapsing section named 'thing':\n"
        "Failed collapsing section key 'content':\n"
        "Failed converting argument 'class' to callable:\n"
        "'spork' is not callable",
        manager.get_default,
        "drawer",
    )
    check_error(
        "Collapsing defaults for 'broken':\n"
        "Collapsing section named 'thing':\n"
        "Failed collapsing section key 'content':\n"
        "Failed converting argument 'class' to callable:\n"
        "'spork' is not callable",
        manager.get_default,
        "broken",
    )


def test_instantiate_broken_ref():
    @configurable(typename="drawer")
    def broken():
        raise errors.ComplexInstantiationError("broken")

    manager = central.ConfigManager(
        [
            {
                "one": basics.HardCodedConfigSection(
                    {
                        "class": drawer,
                        "content": basics.HardCodedConfigSection({"class": broken}),
                    }
                ),
                "multi": basics.HardCodedConfigSection(
                    {
                        "class": drawer,
                        "contents": [basics.HardCodedConfigSection({"class": broken})],
                    }
                ),
            }
        ]
    )
    check_error(
        "Failed instantiating section 'one':\n"
        "Instantiating reference 'content' pointing at None:\n"
        "Failed instantiating section None:\n"
        "Failed instantiating section None: exception caught from 'tests.config.test_central.broken':\n"
        "'broken', callable unset!",
        manager.collapse_named_section("one").instantiate,
    )
    check_error(
        "Failed instantiating section 'multi':\n"
        "Instantiating reference 'contents' pointing at None:\n"
        "Failed instantiating section None:\n"
        "Failed instantiating section None: exception caught from 'tests.config.test_central.broken':\n"
        "'broken', callable unset!",
        manager.collapse_named_section("multi").instantiate,
    )


def test_autoload_instantiationerror():
    @configurable(typename="configsection")
    def broken():
        raise errors.ComplexInstantiationError("broken")

    check_error(
        "Failed loading autoload section 'autoload_broken':\n"
        "Failed instantiating section 'autoload_broken':\n"
        "Failed instantiating section 'autoload_broken': exception caught from 'tests.config.test_central.broken':\n"
        "'broken', callable unset!",
        central.ConfigManager,
        [{"autoload_broken": basics.HardCodedConfigSection({"class": broken})}],
    )


def test_autoload_uncollapsable():
    check_error(
        "Failed collapsing autoload section 'autoload_broken':\n"
        "Collapsing section named 'autoload_broken':\n"
        "Failed converting argument 'class' to callable:\n"
        "'spork' is not callable",
        central.ConfigManager,
        [{"autoload_broken": basics.HardCodedConfigSection({"class": "spork"})}],
    )


def test_autoload_wrong_type():
    check_error(
        "Section 'autoload_wrong' is marked as autoload but type is "
        "drawer, not configsection",
        central.ConfigManager,
        [{"autoload_wrong": basics.HardCodedConfigSection({"class": drawer})}],
    )


def test_lazy_refs():
    @configurable(
        types={"myrepo": "lazy_ref:repo", "thing": "lazy_ref"}, typename="repo"
    )
    def reporef(myrepo=None, thing=None):
        return myrepo, thing

    @configurable(
        types={"myrepo": "lazy_refs:repo", "thing": "lazy_refs"}, typename="repo"
    )
    def reporefs(myrepo=None, thing=None):
        return myrepo, thing

    @configurable(typename="repo")
    def myrepo():
        return "repo!"

    manager = central.ConfigManager(
        [
            {
                "myrepo": basics.HardCodedConfigSection({"class": myrepo}),
                "drawer": basics.HardCodedConfigSection({"class": drawer}),
                "right": basics.AutoConfigSection(
                    {"class": reporef, "myrepo": "myrepo"}
                ),
                "wrong": basics.AutoConfigSection(
                    {"class": reporef, "myrepo": "drawer"}
                ),
            }
        ]
    )
    check_error(
        "reference 'drawer' should be of type 'repo', got 'drawer'",
        manager.objects.repo["wrong"][0].collapse,
    )
    assert "repo!" == manager.objects.repo["right"][0].instantiate()

    manager = central.ConfigManager(
        [
            {
                "myrepo": basics.HardCodedConfigSection({"class": myrepo}),
                "drawer": basics.HardCodedConfigSection({"class": drawer}),
                "right": basics.AutoConfigSection(
                    {"class": reporefs, "myrepo": "myrepo"}
                ),
                "wrong": basics.AutoConfigSection(
                    {"class": reporefs, "myrepo": "drawer"}
                ),
            }
        ]
    )
    check_error(
        "reference 'drawer' should be of type 'repo', got 'drawer'",
        manager.objects.repo["wrong"][0][0].collapse,
    )
    assert ["repo!"] == [c.instantiate() for c in manager.objects.repo["right"][0]]


def test_inherited_default():
    manager = central.ConfigManager(
        [
            {
                "default": basics.HardCodedConfigSection(
                    {
                        "default": True,
                        "inherit": ["basic"],
                    }
                ),
                "uncollapsable": basics.HardCodedConfigSection(
                    {
                        "default": True,
                        "inherit": ["spork"],
                        "inherit-only": True,
                    }
                ),
                "basic": basics.HardCodedConfigSection({"class": drawer}),
            }
        ],
        [RemoteSource()],
    )
    assert manager.get_default("drawer")


def test_section_names():
    manager = central.ConfigManager(
        [
            {
                "thing": basics.HardCodedConfigSection({"class": drawer}),
            }
        ],
        [RemoteSource()],
    )
    collapsed = manager.collapse_named_section("thing")
    assert "thing" == collapsed.name


def test_inherit_only():
    manager = central.ConfigManager(
        [
            {
                "source": basics.HardCodedConfigSection(
                    {
                        "class": drawer,
                        "inherit-only": True,
                    }
                ),
                "target": basics.HardCodedConfigSection(
                    {
                        "inherit": ["source"],
                    }
                ),
            }
        ],
        [RemoteSource()],
    )
    check_error(
        "Collapsing section named 'source':\ncannot collapse inherit-only section",
        manager.collapse_named_section,
        "source",
    )
    assert manager.collapse_named_section("target")


def test_self_inherit():
    section = basics.HardCodedConfigSection({"inherit": ["self"]})
    manager = central.ConfigManager(
        [
            {
                "self": basics.ConfigSectionFromStringDict(
                    {"class": "tests.config.test_central.drawer", "inherit": "self"}
                ),
            }
        ],
        [RemoteSource()],
    )
    check_error(
        "Collapsing section named 'self':\nSelf-inherit 'self' cannot be found",
        get_config_obj,
        manager,
        "drawer",
        "self",
    )
    check_error(
        "Self-inherit 'self' cannot be found", manager.collapse_section, [section]
    )

    manager = central.ConfigManager(
        [
            {
                "self": basics.HardCodedConfigSection(
                    {
                        "inherit": ["self"],
                    }
                )
            },
            {
                "self": basics.HardCodedConfigSection(
                    {
                        "inherit": ["self"],
                    }
                )
            },
            {"self": basics.HardCodedConfigSection({"class": drawer})},
        ]
    )
    assert manager.collapse_named_section("self")
    assert manager.collapse_section([section])
