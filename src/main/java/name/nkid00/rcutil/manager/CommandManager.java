package name.nkid00.rcutil.manager;

import static net.minecraft.server.command.CommandManager.argument;
import static net.minecraft.server.command.CommandManager.literal;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;

import name.nkid00.rcutil.Options;
import name.nkid00.rcutil.command.Rcu;
import name.nkid00.rcutil.command.RcuInterface;
import name.nkid00.rcutil.command.RcuLang;
import name.nkid00.rcutil.command.RcuNew;
import name.nkid00.rcutil.command.RcuReload;
import name.nkid00.rcutil.command.RcuRemove;
import name.nkid00.rcutil.command.RcuRun;
import name.nkid00.rcutil.command.RcuScript;
import name.nkid00.rcutil.helper.ArgumentHelper;
import net.minecraft.command.CommandRegistryAccess;
import net.minecraft.server.command.CommandManager.RegistrationEnvironment;
import net.minecraft.server.command.ServerCommandSource;

public class CommandManager {
    public static void init(CommandDispatcher<ServerCommandSource> dispatcher,
            CommandRegistryAccess registryAccess,
            RegistrationEnvironment environment) {
        // /rcu
        dispatcher.register(literal("rcu")
                .requires((s) -> s.hasPermissionLevel(Options.requiredPermissionLevel()))
                .executes(Rcu::execute));
        // /rcu new <interface name> [option...]
        dispatcher.register(literal("rcu")
                .then(literal("new")
                        .then(argument("interface name", StringArgumentType.word())
                                .executes(RcuNew::execute)
                                .then(argument("option...",
                                        StringArgumentType.greedyString())
                                        .executes(RcuNew::execute)))));
        // /rcu remove <interface name...>
        dispatcher.register(literal("rcu")
                .then(literal("remove")
                        .then(argument("interface name...", StringArgumentType.greedyString())
                                .suggests(ArgumentHelper.uniqueMulti(InterfaceManager::getSuggestions))
                                .executes(RcuRemove::execute))));
        // /rcu interface [interface name...]
        dispatcher.register(literal("rcu")
                .then(literal("interface")
                        .executes(RcuInterface::execute)
                        .then(argument("interface name...", StringArgumentType.greedyString())
                                .suggests(ArgumentHelper.uniqueMulti(InterfaceManager::getSuggestions))
                                .executes(RcuInterface::executeDetail))));
        // /rcu script [script name...]
        dispatcher.register(literal("rcu")
                .then(literal("script")
                        .executes(RcuScript::execute)
                        .then(argument("script name...", StringArgumentType.greedyString())
                                .suggests(ArgumentHelper.uniqueMulti(ScriptManager::getSuggestions))
                                .executes(RcuScript::executeDetail))));
        // /rcu run <script name> [argument...]
        dispatcher.register(literal("rcu")
                .then(literal("run")
                        .then(argument("script name", StringArgumentType.word())
                                .suggests(ScriptManager::getSuggestions)
                                .executes(RcuRun::execute)
                                .then(argument("argument...", StringArgumentType.greedyString())
                                        .suggests(ArgumentHelper.repeatableMulti(ArgumentHelper.merge(
                                                InterfaceManager::getSuggestions,
                                                ScriptManager::getSuggestions)))
                                        .executes(RcuRun::execute)))));
        // /rcu reload
        dispatcher.register(literal("rcu")
                .then(literal("reload")
                        .executes(RcuReload::execute)));
        // /rcu lang <language>
        dispatcher.register(literal("rcu")
                .then(literal("lang")
                        .executes(RcuLang::executeGet)
                        .then(argument("language", StringArgumentType.word())
                                .suggests(LanguageManager::getSuggestions)
                                .executes(RcuLang::executeSet))));
    }
}
