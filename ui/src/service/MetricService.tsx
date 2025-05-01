import {
  errorResponse,
  ResponseContainer,
} from "ecfr-analyzer/data/ResponseContainer";
import { TitleMetricResponse } from "ecfr-analyzer/data/TitleMetricResponse";
import { AgencyMetrics } from "ecfr-analyzer/data/AgencyMetrics";
import { Agency } from "ecfr-analyzer/data/Agency";

const apiRoot = process.env.NEXT_PUBLIC_ECFR_SERVICE_API_URL || "http://localhost:8090/ecfr-service";
const defaultRevalidate = 60 * 60; // seconds

export async function fetchTitleMetrics(): Promise<
  ResponseContainer<TitleMetricResponse>
> {
  try {
    const response = await fetch(`${apiRoot}/metrics/titles`, {
      next: {
        revalidate: defaultRevalidate,
      },
    });

    if (!response.ok) {
      return errorResponse({
        code: response.status,
        message: `Failed to fetch title metrics: ${response.statusText}`,
      });
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching title metrics:", error);
    return errorResponse({
      code: 500,
      message: `Failed to fetch title metrics: ${error}`,
    });
  }
}

export async function fetchAgencyMetrics(): Promise<
  ResponseContainer<AgencyMetrics[]>
> {
  try {
    const response = await fetch(`${apiRoot}/metrics/agencies`, {
      next: {
        revalidate: defaultRevalidate,
      },
    });

    if (!response.ok) {
      return errorResponse({
        code: response.status,
        message: `Failed to fetch agency metrics: ${response.statusText}`,
      });
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching agency metrics:", error);
    return errorResponse({
      code: 500,
      message: `Failed to fetch agency metrics: ${error}`,
    });
  }
}

export async function fetchMetricsForAgency(
  slug: string,
): Promise<ResponseContainer<AgencyMetrics>> {
  try {
    const response = await fetch(`${apiRoot}/metrics/agencies/${slug}`, {
      next: {
        revalidate: defaultRevalidate,
      },
    });

    if (!response.ok) {
      return errorResponse({
        code: response.status,
        message: `Failed to fetch metrics for agency ${slug}: ${response.statusText}`,
      });
    }

    return await response.json();
  } catch (error) {
    console.error(`Error fetching metrics for agency ${slug}:`, error);
    return errorResponse({
      code: 500,
      message: `Failed to fetch metrics for agency ${slug}: ${error}`,
    });
  }
}

export async function fetchSubAgencyMetrics(
  slug: string,
): Promise<ResponseContainer<AgencyMetrics[]>> {
  try {
    const response = await fetch(
      `${apiRoot}/metrics/agencies/${slug}/sub-agencies`,
      {
        next: {
          revalidate: defaultRevalidate,
        },
      },
    );

    if (!response.ok) {
      return errorResponse({
        code: response.status,
        message: `Failed to fetch sub-agency metrics for ${slug}: ${response.statusText}`,
      });
    }

    return await response.json();
  } catch (error) {
    console.error(`Error fetching sub-agency metrics for ${slug}:`, error);
    return errorResponse({
      code: 500,
      message: `Failed to fetch sub-agency metrics for ${slug}: ${error}`,
    });
  }
}
