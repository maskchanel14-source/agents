import { NextResponse } from "next/server";
import { aggregateStatsAsync } from "@/lib/store";
export async function GET() { return NextResponse.json(await aggregateStatsAsync()); }
