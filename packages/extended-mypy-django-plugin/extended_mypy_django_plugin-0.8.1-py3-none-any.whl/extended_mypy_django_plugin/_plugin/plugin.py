import functools
from typing import Generic, TypeVar

from mypy.nodes import Import, ImportAll, ImportFrom, MypyFile
from mypy.options import Options
from mypy.plugin import AnalyzeTypeContext, MethodContext, ReportConfigContext
from mypy.types import Type as MypyType
from mypy_django_plugin import main

from . import analyze, annotation_resolver, config, hook, protocols, type_checker

T_Report = TypeVar("T_Report", bound=protocols.Report)


class PlainHook(
    Generic[T_Report, hook.T_Ctx, hook.T_Ret],
    hook.PlainHook["ExtendedMypyStubs[T_Report]", hook.T_Ctx, hook.T_Ret],
):
    pass


class HookWithExtra(
    Generic[T_Report, hook.T_Ctx, hook.T_Extra, hook.T_Ret],
    hook.HookWithExtra["ExtendedMypyStubs[T_Report]", hook.T_Ctx, hook.T_Extra, hook.T_Ret],
):
    pass


class ExtendedMypyStubs(Generic[T_Report], main.NewSemanalDjangoPlugin):
    """
    The ``ExtendedMypyStubs`` mypy plugin extends the
    ``mypy_django_plugin.main.NewSemanalDjangoPlugin`` found in the active python
    environment.

    It implements the following mypy plugin hooks:

    .. automethod:: report_config_data
        :no-index:

    .. automethod:: get_additional_deps
        :no-index:

    .. autoattribute:: get_type_analyze_hook
        :no-index:

    .. autoattribute:: get_attribute_hook
        :no-index:

    .. autoattribute:: get_method_hook
        :no-index:
    """

    @classmethod
    def make_virtual_dependency_report(
        cls,
        *,
        extra_options: config.ExtraOptions,
        virtual_dependency_handler: protocols.VirtualDependencyHandler[protocols.T_Report],
    ) -> protocols.CombinedReport[protocols.T_Report]:
        return virtual_dependency_handler(
            project_root=extra_options.project_root,
            django_settings_module=extra_options.django_settings_module,
            virtual_deps_destination=extra_options.scratch_path,
        )

    def __init__(
        self,
        options: Options,
        mypy_version_tuple: tuple[int, int],
        virtual_dependency_handler: protocols.VirtualDependencyHandler[T_Report],
    ) -> None:
        self.options = options
        self.extra_options = config.ExtraOptions.from_config(options.config_file)
        self.mypy_version_tuple = mypy_version_tuple

        self.virtual_dependency_report = self.make_virtual_dependency_report(
            extra_options=self.extra_options, virtual_dependency_handler=virtual_dependency_handler
        )

        make_resolver: protocols.ResolverMaker = functools.partial(
            annotation_resolver.make_resolver,
            get_concrete_aliases=self.virtual_dependency_report.report.get_concrete_aliases,
            get_queryset_aliases=self.virtual_dependency_report.report.get_queryset_aliases,
            plugin_lookup_fully_qualified=self.lookup_fully_qualified,
        )

        self.analyzer = analyze.Analyzer(make_resolver=make_resolver)
        self.type_checker = type_checker.TypeChecking(make_resolver=make_resolver)

        super().__init__(options)

        self.extra_init()

    def extra_init(self) -> None:
        """
        Place to add extra logic after __init__
        """

    def report_config_data(self, ctx: ReportConfigContext) -> dict[str, object]:
        """
        Add our extra options to the report config data, so that mypy knows to clear the cache
        if those settings change.
        """
        return {
            **super().report_config_data(ctx),
            "extended_mypy_django_plugin": self.extra_options.for_report(),
        }

    def get_additional_deps(self, file: MypyFile) -> list[tuple[int, str, int]]:
        """
        Ensure that models are re-analyzed if any other models that depend on
        them change.

        We use a generated "report" to re-analyze a file if a new dependency
        is discovered after this file has been processed.
        """
        file_import = file.fullname
        full_imports: set[str] = set()

        self.virtual_dependency_report.ensure_virtual_dependency(module_import_path=file.fullname)

        for imp in file.imports:
            if isinstance(imp, ImportFrom | ImportAll):
                if imp.relative:
                    prefix_base = ".".join(file_import.split(".")[: -imp.relative])
                    prefix = f"{prefix_base}.{imp.id}"
                else:
                    prefix = imp.id

                if isinstance(imp, ImportAll):
                    # This is the best we can do unfortunately
                    full_imports.add(prefix)
                else:
                    for name, _ in imp.names:
                        full_imports.add(f"{prefix}.{name}")

            elif isinstance(imp, Import):
                for name, _ in imp.ids:
                    full_imports.add(name)

        if self.options.use_fine_grained_cache:
            using_incremental_cache = False
        else:
            using_incremental_cache = (
                self.options.incremental and self.options.cache_dir != "/dev/null"
            )

        return list(
            self.virtual_dependency_report.report.additional_deps(
                file_import_path=file_import,
                imports=full_imports,
                django_settings_module=self.extra_options.django_settings_module,
                using_incremental_cache=using_incremental_cache,
                super_deps=super().get_additional_deps(file),
            )
        )

    @hook.hook
    class get_type_analyze_hook(
        HookWithExtra[T_Report, AnalyzeTypeContext, protocols.KnownAnnotations, MypyType]
    ):
        """
        Resolve classes annotated with ``Concrete`` or ``DefaultQuerySet``.
        """

        def choose(
            self, *, fullname: str, super_hook: hook.MypyHook[AnalyzeTypeContext, MypyType]
        ) -> hook.Choice[protocols.KnownAnnotations]:
            annotation = protocols.KnownAnnotations.resolve(fullname)
            if annotation is not None:
                return True, annotation
            else:
                return False

        def run(
            self,
            ctx: AnalyzeTypeContext,
            *,
            fullname: str,
            super_hook: hook.MypyHook[AnalyzeTypeContext, MypyType],
            extra: protocols.KnownAnnotations,
        ) -> MypyType:
            return self.plugin.analyzer.analyze_type(ctx, extra)

    @hook.hook
    class get_method_hook(PlainHook[T_Report, MethodContext, MypyType]):
        """
        Used to ensure Concrete.cast_as_concrete returns the appropriate type.
        """

        def choose(
            self, *, fullname: str, super_hook: hook.MypyHook[MethodContext, MypyType]
        ) -> bool:
            class_name, _, method_name = fullname.rpartition(".")
            if method_name == "cast_as_concrete":
                info = self.plugin._get_typeinfo_or_none(class_name)
                if info and info.has_base(protocols.KnownClasses.CONCRETE.value):
                    return True

            return False

        def run(self, ctx: MethodContext) -> MypyType:
            return self.plugin.type_checker.modify_cast_as_concrete(ctx)
