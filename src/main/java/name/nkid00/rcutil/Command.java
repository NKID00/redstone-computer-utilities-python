package name.nkid00.rcutil;

import java.util.Iterator;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;

import org.lwjgl.system.CallbackI.V;

import net.minecraft.entity.Entity;
import net.minecraft.item.ItemStack;
import net.minecraft.server.command.ServerCommandSource;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.text.LiteralText;
import net.minecraft.text.MutableText;
import net.minecraft.text.Texts;
import net.minecraft.text.TranslatableText;
import net.minecraft.util.Formatting;
import name.nkid00.rcutil.suggestion.RamSuggestionProvider;
import name.nkid00.rcutil.enumeration.EdgeTriggering;
import name.nkid00.rcutil.enumeration.Status;
import name.nkid00.rcutil.rambus.RamBus;
import name.nkid00.rcutil.rambus.RamBusBuilder;
import name.nkid00.rcutil.rambus.RoRamBusBuilder;
import name.nkid00.rcutil.rambus.WoRamBusBuilder;

import static net.minecraft.server.command.CommandManager.literal;
import static net.minecraft.server.command.CommandManager.argument;

public class Command {
    public static void register(CommandDispatcher<ServerCommandSource> dispatcher, boolean dedicated) {
        dispatcher.register(
            literal("rcu")
            .requires((s) -> s.hasPermissionLevel(RCUtil.requiredPermissionLevel))
            // give wand or stop running command
            .executes(Command::executeRcu)
            .then(
                literal("fileram")
                // list rams
                .executes(Command::executeRcuRam)
                .then(
                    literal("new")
                    .then(
                        // read-only
                        literal("ro")
                        .then(
                            // positive edge triggering clock
                            literal("pos")
                            .then(
                                argument("name", StringArgumentType.string())
                                .then(
                                    argument("file", StringArgumentType.string())
                                    .executes((c) -> executeRcuFileRamNew(c, EdgeTriggering.Positive, RoRamBusBuilder.class))
                                )
                            )
                        )
                        .then(
                            // negative edge triggering clock
                            literal("neg")
                            .then(
                                argument("name", StringArgumentType.string())
                                .then(
                                    argument("file", StringArgumentType.string())
                                    .executes((c) -> executeRcuFileRamNew(c, EdgeTriggering.Negative, RoRamBusBuilder.class))
                                )
                            )
                        )
                        .then(
                            // dual edge triggering clock
                            literal("dual")
                            .then(
                                argument("name", StringArgumentType.string())
                                .then(
                                    argument("file", StringArgumentType.string())
                                    .executes((c) -> executeRcuFileRamNew(c, EdgeTriggering.Dual, RoRamBusBuilder.class))
                                )
                            )
                        )
                    )
                    .then(
                        // write-only
                        literal("wo")
                        .then(
                            // positive edge triggering clock
                            literal("pos")
                            .then(
                                argument("name", StringArgumentType.string())
                                .then(
                                    argument("file", StringArgumentType.string())
                                    .executes((c) -> executeRcuFileRamNew(c, EdgeTriggering.Positive, WoRamBusBuilder.class))
                                )
                            )
                        )
                        .then(
                            // negative edge triggering clock
                            literal("neg")
                            .then(
                                argument("name", StringArgumentType.string())
                                .then(
                                    argument("file", StringArgumentType.string())
                                    .executes((c) -> executeRcuFileRamNew(c, EdgeTriggering.Negative, WoRamBusBuilder.class))
                                )
                            )
                        )
                        .then(
                            // dual edge triggering clock
                            literal("dual")
                            .then(
                                argument("name", StringArgumentType.string())
                                .then(
                                    argument("file", StringArgumentType.string())
                                    .executes((c) -> executeRcuFileRamNew(c, EdgeTriggering.Dual, WoRamBusBuilder.class))
                                )
                            )
                        )
                    )
                )
                .then(
                    literal("remove")
                    .then(
                        argument("name", StringArgumentType.string())
                        .suggests(new RamSuggestionProvider())
                        .executes(Command::executeRcuFileRamRemove)
                    )
                )
            )
        );
    }

    private static int executeRcu(CommandContext<ServerCommandSource> c) {
        ServerCommandSource s = c.getSource();
        if (RCUtil.status == Status.Idle) {
            Entity entity = s.getEntity();
            if (entity != null && entity instanceof ServerPlayerEntity) {
                if (((ServerPlayerEntity)entity).inventory.insertStack(new ItemStack(RCUtil.wandItem))) {
                    s.sendFeedback(new TranslatableText("rcutil.commands.rcu.success.item", RCUtil.wandItemHoverableText), true);
                    return 1;
                } else {
                    s.sendError(new TranslatableText("rcutil.commands.rcu.failed.item"));
                    return 0;
                }
            } else {
                s.sendError(new TranslatableText("rcutil.commands.rcu.failed.stop"));
                return 0;
            }
        } else {
            RCUtil.status = Status.Idle;
            s.sendFeedback(new TranslatableText("rcutil.commands.rcu.success.stop"), true);
            return 1;
        }
    }

    private static int executeRcuRam(CommandContext<ServerCommandSource> c) {
        ServerCommandSource s = c.getSource();
        int roCount = RCUtil.roRams.size();
        int woCount = RCUtil.woRams.size();
        if (roCount == 0 && woCount == 0) {
            s.sendError(new TranslatableText("rcutil.commands.rcu.fileram.failed"));
            return 0;
        } else {
            MutableText text;
            if (roCount == 0) {
                text = new TranslatableText("rcutil.commands.rcu.fileram.none");
            } else {
                text = new LiteralText("");
                Iterator<String> iter = RCUtil.roRams.keySet().iterator();
                for (int i = 0; ; i++) {
                    String k = iter.next();
                    RamBus v = RCUtil.roRams.get(k);
                    MutableText t = new LiteralText(k);
                    if (v.running) {
                        t.formatted(Formatting.BOLD, Formatting.UNDERLINE);
                    }
                    text.append(t);
                    if (i >= roCount) {
                        break;
                    }
                    text.append(", ");
                }
            }
            s.sendFeedback(new TranslatableText("rcutil.commands.rcu.fileram.success.ro", roCount, text), false);
            if (woCount == 0) {
                text = new TranslatableText("rcutil.commands.rcu.fileram.none");
            } else {
                text = new LiteralText("");
                Iterator<String> iter = RCUtil.roRams.keySet().iterator();
                for (int i = 0; ; i++) {
                    String k = iter.next();
                    RamBus v = RCUtil.woRams.get(k);
                    MutableText t = new LiteralText(k);
                    if (v.running) {
                        t.formatted(Formatting.BOLD, Formatting.UNDERLINE);
                    }
                    text.append(t);
                    text.append(Texts.bracketed(new LiteralText(v.filename)));
                    if (i >= roCount) {
                        break;
                    }
                    text.append(", ");
                }
            }
            s.sendFeedback(new TranslatableText("rcutil.commands.rcu.fileram.success.wo", woCount, text), false);
            return roCount + woCount;
        }
    }

    private static int executeRcuFileRamNew(CommandContext<ServerCommandSource> c, EdgeTriggering clockEdgeTriggering, Class<?> ramBusBuilder) {
        ServerCommandSource s = c.getSource();
        String name = StringArgumentType.getString(c, "name");
        if (RCUtil.roRams.keySet().contains(name)) {
            s.sendError(new TranslatableText("rcutil.commands.rcu.fileram.new.failed.name.ro", name));
            return 0;
        } else if (RCUtil.woRams.keySet().contains(name)) {
            s.sendError(new TranslatableText("rcutil.commands.rcu.fileram.new.failed.name.wo", name));
            return 0;
        } else if (RCUtil.status != Status.Idle) {
            s.sendError(new TranslatableText("rcutil.commands.rcu.failed.running"));
            return 0;
        }
        RamBusBuilder builder;
        try {
            builder = (RamBusBuilder)ramBusBuilder.newInstance();
        } catch (IllegalAccessException | InstantiationException e) {  // make compiler happy
            return 0;
        }
        builder.name = name;
        String file = StringArgumentType.getString(c, "file");
        if (!builder.setFile(file)) {
            s.sendError(new TranslatableText("rcutil.commands.rcu.fileram.new.ro.failed.file", file));
            return 0;
        }
        RCUtil.ramBusBuilder = builder;
        RCUtil.status = Status.RamNew1;
        if (ramBusBuilder == RoRamBusBuilder.class) {
            s.sendFeedback(new TranslatableText("rcutil.commands.rcu.fileram.new.ro.start", name), true);
        } else {  // ramBusBuilder == WoRamBusBuilder.class
            s.sendFeedback(new TranslatableText("rcutil.commands.rcu.fileram.new.wo.start", name), true);
        }
        s.sendFeedback(new TranslatableText("rcutil.commands.rcu.fileram.new.step1", RCUtil.wandItemHoverableText), true);
        return 1;
    }

    private static int executeRcuFileRamRemove(CommandContext<ServerCommandSource> c) {
        ServerCommandSource s = c.getSource();
        String name = StringArgumentType.getString(c, "name");
        if (RCUtil.roRams.keySet().contains(name)) {
            RCUtil.roRams.remove(name);
            s.sendFeedback(new TranslatableText("rcutil.commands.rcu.fileram.remove.ro.success", name), true);
            return 1;
        } else if (RCUtil.woRams.keySet().contains(name)) {
            RCUtil.roRams.remove(name);
            s.sendFeedback(new TranslatableText("rcutil.commands.rcu.fileram.remove.wo.success", name), true);
            return 1;
        }
        s.sendError(new TranslatableText("rcutil.commands.rcu.fileram.remove.failed", name)); 
        return 1;
    }
}
