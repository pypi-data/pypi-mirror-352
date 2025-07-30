import os
import sys
import argparse
import textwrap

from ormxl.code_collector import CodeCollector
from ormxl.config import Config
from ormxl.entities import Entity
from ormxl.project import set_templates_directory
from ormxl.profiles_manager import ProfilesManager
from ormxl.subsystem_manager import SubsystemManager
from ormxl.manifest_processor import ManifestProcessor
from ormxl.templates_manager import save_styles, save_tags, save_templates


class CompactHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def __init__(self, *args, **kwargs):
        kwargs["width"] = 100
        kwargs["max_help_position"] = 30
        super().__init__(*args, **kwargs)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            return super()._format_action_invocation(action)
        return ", ".join(action.option_strings)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        prog="DDJCM",
        description="It is 1C in Django world",
        epilog="Good luck!",
        formatter_class=CompactHelpFormatter
    )

    argparser.add_argument(
        "--manifest",
        help="path to manifest file",
        default="manifest.py"
    )
    argparser.add_argument(
        "--lib-path",
        help="path to lib source",
        default=os.getenv("ORMXL_LIB_PATH") or ".venv/Lib/site-packages/ormxl"
    )
    argparser.add_argument(
        "--create-app-command",
        help="command to create an app",
        default="python3 manage.py startapp {app_name}"
    )
    argparser.add_argument(
        "--encoding",
        help="encoding for opening and writing files",
        default="utf-8"
    )
    argparser.add_argument(
        "--guard-start-comment",
        help="acomment to mark beginning of generated code",
        default="# <<<\n"
    )
    argparser.add_argument(
        "--guard-end-comment",
        help="acomment to mark end of generated code",
        default="\n# >>>"
    )
    argparser.add_argument(
        "--tss",
        help="tss...",
        action='store_true',
        default=False
    )
    argparser.add_argument(
        "--generate-template-manifest",
        help="generating templated manifest",
        action='store_true',
        default=False
    )

    args = argparser.parse_args()

    if args.tss:
        print(textwrap.dedent("""
            First of all, you need to add the `APPEND_SLASH = True` setting to settings.py

            Then generate a template manifest to build on during development: --generate-template-manifest

            After generation, please ensure that the urlpatterns are included in all files and that the
            urls.py file is written correctly. There is a definition (urlpatterns = [...]) and an
            appends (urlpatterns += [...]) available.

            Criterias:
                1. Technical Specification (TS) Analysis & Algorithm Design
                    0 - Incorrect/missing algorithm
                    1 - Partial TS analysis, incomplete I/O specs, flowchart inaccuracies
                    2 - Full TS compliance, correct specs, algorithm matches requirements
                2. Algorithm Documentation (Compliance with GOST/ISO)
                    0 - Standards violated
                    1 - Minor deviations
                    2 - Fully compliant
                3. Algorithm Implementation
                    0 - Missing logic, incorrect data usage
                    1 - Partial testing, incomplete flowchart
                    2 - All scenarios covered, I/O data validated
                4. Module Development
                    0 - Not developed
                    1 - Minor deviations from TS
                    2 - Fully TS-compliant
                5. Code Style Guide Adherence
                    0 - Non-intuitive naming, violations
                    1 - Partial compliance
                    2 - Full alignment (naming, clarity)
                6. Error Handling & Debugging
                    0 - Crashes/unhandled errors
                    1 - Partial exception handling, no fatal errors
                    2 - Robust error recovery, stable execution
                7. Debugging Tools & Reporting
                    0 - No tools used
                    1 - Partial debug logs, minimal documentation
                    2 - Full tool usage, detailed report
                8. Test Protocol Documentation
                    0 - Not documented
                    1 - Basic documentation
                    2 - Standard-compliant test report
                9. Functional Testing
                    0 - No tests
                    1 - Partial test coverage
                    2 - Minimum 1 test per function
                10. Testing Tools
                    0 - Not used
                    1 - Partially used
                    2 - Fully utilized
                11. Database Design (3NF, ERD)
                    0 - Critical flaws
                    1 - Minor deviations, meets 3NF
                    2 - Fully compliant, indexed, justified
                12. Queries & Reports
                    0 - Non-functional
                    1 - Partial task alignment
                    2 - Correct output, grouped data
                13. Database Backup/Restore
                    0 - Not done
                    1 - Backup only
                    2 - Backup + point-in-time restore
                14. DB Naming Conventions
                    0 - Non-compliant
                    1 - Partial adherence
                    2 - Industry-standard naming
                15. Database Population
                    0 - Empty/incorrect
                    1 - Partially loaded, errors
                    2 - Fully loaded, valid data
                16. DB Security (Auth/Roles)
                    0 - No protections
                    1 - Partial setup
                    2 - User roles, passwords, groups
                17. Technical Documentation
                    0 - Missing/non-compliant
                    1 - Partial standard adherence
                    2 - Fully standardized
                18. User/Role Management
                    0 - Not configured
                    1 - Partial role alignment
                    2 - Matches job requirements
                19. Software Modifications
                    0 - Not implemented
                    1 - Partially added
                    2 - Fully meets TS updates
                20. Modification Proposals
                    0 - None provided
                    1 - Partial suggestions (text doc)
                    2 - Detailed proposals (text doc)
                21. Component Installation
                    0 - Failed/not done
                    1 - Partial installation
                    2 - Full deployment
                22. Component Configuration
                    0 - Not configured
                    1 - Partial setup
                    2 - Fully configured
                23. Code Quality Metrics
                    0 - No analysis
                    1 - Partial review
                    2 - Full assessment (error handling, tests, comments)
        """))
        sys.exit(0)

    if args.generate_template_manifest:
        with open("Tmanifest.py", "w", encoding="utf-8") as f:
            f.write(textwrap.dedent("""
                from ormxl.system import System
                from ormxl.entities import Entity, String, Integer, Float, Date, Time, DateTime, Foreign, Enum
                from ormxl.permissions import Permission, All, Only, Nobody


                system = System(
                    subsystems={
                        "company": {
                            "name": "Компании",
                            "permission": Permission(),
                        },
                    },
                    roles={
                        "user": "Пользователь",
                        "manager": "Менеджер",
                        "admin": "Администратор",
                    },
                    entities={
                        "founder": Entity(
                            verbose="учредитель",
                            verboses="учредители",
                            subsystem="company",
                            fields={
                                "name": String(verbose="Имя")
                            },
                            lists={},
                            prefill_create="company.all_companies",  # subsystem dot list
                            prefill_create_title="Создать компанию",
                        ),
                        "company": Entity(
                            verbose="компания",
                            verboses="компании",
                            subsystem="company",
                            fields={
                                "name": String(
                                    verbose="Название",
                                ),
                                "comment": String(
                                    verbose="Комментарий",
                                    permission=Permission(edit=Only("user")),
                                ),
                                "invest": Integer(verbose="Курс акций", permission=Permission(edit=Only("admin"))),
                                "temp": Float(verbose="Температура в здании", permission=Permission(edit=Only("admin"))),
                                "born_date": Date(verbose="Дата основания", permission=Permission(edit=Only("admin"))),
                                "bort_time": Time(verbose="Время основания", permission=Permission(edit=Only("admin"))),
                                "sex": Enum(
                                    verbose="Пол",
                                    choices={
                                        "male": "Муж",
                                        "female": "Жен",
                                    },
                                ),
                                "last_update": DateTime(verbose="Последнее обновление", permission=Permission(edit=Only("admin"))),
                                "founder": Foreign(
                                    verbose="Учредитель",
                                    to="company.Founder",
                                    on_delete="cascade",
                                    queryset="Founder.objects.all()",
                                    permission=Permission(edit=Nobody()),
                                ),
                            },
                            lists={
                                "all_companies": {
                                    "name": "Все компании",
                                    "permission": Permission(edit=Only("user")),
                                    "queryset": "all()",
                                    "fields": ["name", "comment"],
                                    "create": ["name", "founder"],
                                    "create_title": "Создать компанию",
                                    "reports": {
                                        "all_companies": {
                                            "verbose": "Отчет \"Все компании\"",
                                            "queryset": "all()",
                                            "fields": ["name", "comment"],
                                            "permission": Permission()
                                        },
                                    },
                                },
                            },
                            reports={
                                "company": {
                                    "verbose": "Отчет \"О компании\"",
                                    "queryset": "get(pk=model_id)",  # u can use variable model_id by deafault for pass id of model
                                    "fields": ["name", "comment"],
                                    "permission": Permission()
                                },
                            },
                            prefill_actor="company.Founder",  # subsystem dot entity
                        ),
                    },
                )
            """))
        sys.exit(0)

    config = Config(
        lib_path=args.lib_path,
        create_app_command=args.create_app_command,
        encoding=args.encoding,
        guard_start_comment=args.guard_start_comment,
        guard_end_comment=args.guard_end_comment
    )

    set_templates_directory(config)
    save_templates(config)

    manifest_processor = ManifestProcessor(args.manifest.split(".")[0])

    for subsystem in manifest_processor.get_subsystems():
        save_tags(subsystem, config)
        save_styles (subsystem, config)


    code_collector = CodeCollector(config)

    profiles_manager = ProfilesManager(roles=manifest_processor.get_roles(), code_collector=code_collector, config=config)

    profiles_manager.create_app()
    profiles_manager.create_model()
    profiles_manager.create_forms()
    profiles_manager.create_views()
    profiles_manager.save_urls()

    save_styles ("profiles", config)

    subsystem_manager = SubsystemManager(manifest_processor.get_subsystems(), code_collector, config)
    subsystem_manager.create_apps()
    subsystem_manager.create_dashboard(manifest_processor.get_roles())
    subsystem_manager.register_delete_result_view()

    entity: Entity
    for name, entity in manifest_processor.get_entities().items():
        entity.set_name(name)
        entity.set_config(config)
        entity.set_roles(manifest_processor.get_roles())
        entity.set_code_collector(code_collector)

        entity.create_model()

        entity.save_forms()
        entity.save_views()
        entity.register_urls()

    subsystem_manager.create_entities_lists(manifest_processor.get_entities(), manifest_processor.get_roles())

    code_collector.write()
